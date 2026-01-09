#!/usr/bin/env python3
"""Evolution Feedback Loop - Self-Evolving Context Engineering

"모든 작업 결과 → 메트릭 수집 → 템플릿 개선 → 진화"

This hook captures metrics from completed work and feeds them back
to improve future specifications, routing, and estimations.

Triggers: PostToolUse (Edit|Write), Stop
Output: Metrics stored in .claude/knowledge/evolution/

Metrics Captured:
- planned_vs_actual_duration
- estimated_vs_actual_complexity
- predicted_vs_actual_files_changed
- agent_routing_decisions
- spec_accuracy_score
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent))
try:
    from utils import (
        get_project_dir, get_claude_dir, ensure_dir,
        safe_read_file, safe_write_file, get_full_timestamp
    )
except ImportError:
    # Fallback implementations
    def get_project_dir() -> Path:
        return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

    def get_claude_dir() -> Path:
        return get_project_dir() / ".claude"

    def ensure_dir(path) -> Path:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def safe_read_file(path, default="") -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except:
            return default

    def safe_write_file(path, content) -> bool:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return True
        except:
            return False

    def get_full_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")


# ═══════════════════════════════════════════════════════════════════════════
# EVOLUTION METRICS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

EVOLUTION_DIR = "knowledge/evolution"
METRICS_FILE = "session-metrics.json"
PATTERNS_FILE = "learned-patterns.md"
ROUTING_LOG = "routing-decisions.json"

# Improvement thresholds
DEGRADATION_THRESHOLD = 0.10  # 10% degradation triggers rollback
IMPROVEMENT_TARGET = 0.05     # 5% improvement per iteration


# ═══════════════════════════════════════════════════════════════════════════
# METRICS COLLECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_evolution_dir() -> Path:
    """Get or create evolution metrics directory"""
    evolution_dir = get_claude_dir() / EVOLUTION_DIR
    ensure_dir(evolution_dir)
    return evolution_dir


def load_session_metrics() -> dict:
    """Load current session metrics"""
    metrics_path = get_evolution_dir() / METRICS_FILE
    content = safe_read_file(metrics_path, "{}")
    try:
        return json.loads(content)
    except:
        return {}


def save_session_metrics(metrics: dict) -> bool:
    """Save session metrics"""
    metrics_path = get_evolution_dir() / METRICS_FILE
    metrics["last_updated"] = get_full_timestamp()
    return safe_write_file(metrics_path, json.dumps(metrics, indent=2, ensure_ascii=False))


def collect_file_metrics() -> dict:
    """Collect metrics about file changes in session"""
    project_dir = get_project_dir()
    claude_dir = get_claude_dir()

    metrics = {
        "files_modified": 0,
        "files_created": 0,
        "total_lines_changed": 0,
    }

    # Check git diff for changes (if in git repo)
    try:
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--stat", "--cached"],
            capture_output=True,
            text=True,
            cwd=project_dir,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout
            # Parse git diff stat
            lines = output.strip().split('\n')
            for line in lines[:-1]:  # Skip summary line
                if '|' in line:
                    metrics["files_modified"] += 1
                    # Extract number of changes
                    match = re.search(r'\|\s*(\d+)', line)
                    if match:
                        metrics["total_lines_changed"] += int(match.group(1))
    except:
        pass

    return metrics


def collect_task_metrics() -> dict:
    """Collect metrics about completed tasks"""
    claude_dir = get_claude_dir()
    todo_file = claude_dir / "todo.md"

    metrics = {
        "tasks_completed": 0,
        "tasks_pending": 0,
        "tasks_blocked": 0,
    }

    if todo_file.exists():
        content = safe_read_file(todo_file)
        metrics["tasks_completed"] = len(re.findall(r'- \[x\]', content))
        metrics["tasks_pending"] = len(re.findall(r'- \[ \]', content))
        # Look for blocked indicators
        metrics["tasks_blocked"] = content.lower().count("blocked") + content.lower().count("waiting")

    return metrics


def collect_spec_accuracy() -> Optional[dict]:
    """Compare spec predictions vs actual outcomes"""
    claude_dir = get_claude_dir()

    # Look for spec files
    spec_dir = claude_dir / "specs"
    if not spec_dir.exists():
        return None

    accuracy = {
        "specs_found": 0,
        "tasks_predicted": 0,
        "tasks_actual": 0,
        "files_predicted": 0,
        "files_actual": 0,
        "accuracy_score": 0.0,
    }

    # This is a simplified version - actual implementation would
    # parse spec files and compare with git history
    for spec_file in spec_dir.glob("*.md"):
        accuracy["specs_found"] += 1
        content = safe_read_file(spec_file)

        # Count predicted tasks
        accuracy["tasks_predicted"] += len(re.findall(r'TASK-\d+', content))

        # Count predicted files
        accuracy["files_predicted"] += len(re.findall(r'`[^`]+\.(ts|js|py|md)`', content))

    # Get actual from git
    file_metrics = collect_file_metrics()
    accuracy["files_actual"] = file_metrics["files_modified"]

    task_metrics = collect_task_metrics()
    accuracy["tasks_actual"] = task_metrics["tasks_completed"]

    # Calculate accuracy score
    if accuracy["tasks_predicted"] > 0:
        task_accuracy = min(1.0, accuracy["tasks_actual"] / accuracy["tasks_predicted"])
    else:
        task_accuracy = 1.0 if accuracy["tasks_actual"] == 0 else 0.5

    if accuracy["files_predicted"] > 0:
        file_accuracy = min(1.0, accuracy["files_actual"] / accuracy["files_predicted"])
    else:
        file_accuracy = 1.0 if accuracy["files_actual"] == 0 else 0.5

    accuracy["accuracy_score"] = (task_accuracy + file_accuracy) / 2

    return accuracy


# ═══════════════════════════════════════════════════════════════════════════
# PATTERN LEARNING
# ═══════════════════════════════════════════════════════════════════════════

def extract_successful_patterns(metrics: dict) -> list[str]:
    """성공한 세션에서 패턴 식별"""
    patterns = []

    # 높은 완료율 패턴
    task_metrics = metrics.get("tasks", {})
    completed = task_metrics.get("tasks_completed", 0)
    pending = task_metrics.get("tasks_pending", 0)

    if completed > 0 and pending == 0:
        patterns.append("✅ 모든 작업 완료 - 좋은 작업 범위 설정")

    if completed > 5:
        patterns.append("⚡ 높은 처리량 세션 - 효과적인 분해")

    # 파일 변경 효율성
    file_metrics = metrics.get("files", {})
    if file_metrics.get("files_modified", 0) <= 3 and completed > 0:
        patterns.append("🎯 집중된 변경 - 원자 작업 원칙 준수")

    # 스펙 정확도
    spec_accuracy = metrics.get("spec_accuracy", {})
    if spec_accuracy:
        score = spec_accuracy.get("accuracy_score", 0)
        if score >= 0.8:
            patterns.append(f"📊 높은 스펙 정확도 ({score:.0%}) - 좋은 추정")
        elif score < 0.5:
            patterns.append(f"⚠️ 낮은 스펙 정확도 ({score:.0%}) - 추정 개선 필요")

    return patterns


def update_learned_patterns(patterns: list[str]) -> bool:
    """Append new patterns to the patterns file"""
    if not patterns:
        return True

    patterns_path = get_evolution_dir() / PATTERNS_FILE
    timestamp = get_full_timestamp()

    content = safe_read_file(patterns_path, "# Learned Patterns\n\n")

    # Add new patterns section
    content += f"\n## Session {timestamp}\n\n"
    for pattern in patterns:
        content += f"- {pattern}\n"

    return safe_write_file(patterns_path, content)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTING OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════

def log_routing_decision(decision: dict) -> bool:
    """Log agent routing decisions for analysis"""
    routing_path = get_evolution_dir() / ROUTING_LOG

    # Load existing log
    content = safe_read_file(routing_path, "[]")
    try:
        log = json.loads(content)
    except:
        log = []

    # Add new decision
    decision["timestamp"] = get_full_timestamp()
    log.append(decision)

    # Keep last 100 decisions
    log = log[-100:]

    return safe_write_file(routing_path, json.dumps(log, indent=2, ensure_ascii=False))


def analyze_routing_effectiveness() -> dict:
    """Analyze routing decision effectiveness"""
    routing_path = get_evolution_dir() / ROUTING_LOG
    content = safe_read_file(routing_path, "[]")

    try:
        log = json.loads(content)
    except:
        return {"error": "No routing data"}

    if not log:
        return {"message": "No routing decisions logged yet"}

    # Count by agent
    agent_counts = {}
    agent_success = {}

    for entry in log:
        agent = entry.get("agent", "unknown")
        success = entry.get("success", True)

        agent_counts[agent] = agent_counts.get(agent, 0) + 1
        if success:
            agent_success[agent] = agent_success.get(agent, 0) + 1

    # Calculate success rates
    success_rates = {}
    for agent, count in agent_counts.items():
        successes = agent_success.get(agent, 0)
        success_rates[agent] = successes / count if count > 0 else 0

    return {
        "total_decisions": len(log),
        "agent_distribution": agent_counts,
        "success_rates": success_rates,
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EVOLUTION LOOP
# ═══════════════════════════════════════════════════════════════════════════

def run_evolution_cycle() -> dict:
    """Run a complete evolution feedback cycle"""
    results = {
        "timestamp": get_full_timestamp(),
        "metrics_collected": False,
        "patterns_learned": [],
        "recommendations": [],
    }

    # 1. Collect all metrics
    metrics = load_session_metrics()

    metrics["files"] = collect_file_metrics()
    metrics["tasks"] = collect_task_metrics()

    spec_accuracy = collect_spec_accuracy()
    if spec_accuracy:
        metrics["spec_accuracy"] = spec_accuracy

    # 2. Save updated metrics
    if save_session_metrics(metrics):
        results["metrics_collected"] = True

    # 3. Extract patterns
    patterns = extract_successful_patterns(metrics)
    results["patterns_learned"] = patterns

    # 4. Update patterns file
    update_learned_patterns(patterns)

    # 5. 권장사항 생성
    if metrics.get("spec_accuracy", {}).get("accuracy_score", 1) < 0.6:
        results["recommendations"].append(
            "더 철저한 스펙 단계 고려 - 추정 정확도가 낮음"
        )

    if metrics.get("tasks", {}).get("tasks_blocked", 0) > 0:
        results["recommendations"].append(
            "일부 작업이 차단됨 - 의존성 식별 개선 필요"
        )

    if metrics.get("files", {}).get("files_modified", 0) > 5:
        results["recommendations"].append(
            "많은 파일 수정됨 - 더 원자적인 작업 분해 고려"
        )

    return results


def output_evolution_summary(results: dict) -> None:
    """진화 요약을 추가 컨텍스트로 출력"""
    summary_parts = []

    if results["patterns_learned"]:
        summary_parts.append("📈 **세션 패턴**:")
        for pattern in results["patterns_learned"][:3]:
            summary_parts.append(f"  {pattern}")

    if results["recommendations"]:
        summary_parts.append("\n💡 **진화 권장사항**:")
        for rec in results["recommendations"][:3]:
            summary_parts.append(f"  - {rec}")

    if summary_parts:
        output = {
            "additionalContext": "\n".join(summary_parts)
        }
        print(json.dumps(output, ensure_ascii=False))


def main():
    """Main entry point for evolution feedback hook"""
    try:
        # Run evolution cycle
        results = run_evolution_cycle()

        # Output summary if there's meaningful feedback
        if results["patterns_learned"] or results["recommendations"]:
            output_evolution_summary(results)

    except Exception as e:
        # Silent failure - don't interrupt the session
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
