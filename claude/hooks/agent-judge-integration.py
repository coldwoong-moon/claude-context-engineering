#!/usr/bin/env python3
"""Agent-as-a-Judge Integration Hook

Automatically trigger Agent-as-a-Judge evaluation after task completion.
Integrates with the evolution feedback loop.

Trigger: Stop hook (after session ends)
Output: Evaluation report stored in .claude/knowledge/evolution/evaluations/
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Import shared utilities (assuming they exist from evolution-feedback.py)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from utils import (
        get_project_dir, get_claude_dir, ensure_dir,
        safe_read_file, safe_write_file, get_full_timestamp
    )
except ImportError:
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
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

EVAL_DIR = "knowledge/evolution/evaluations"
EVAL_INDEX = "evaluation-index.json"

# Evaluation criteria weights (from Agent-as-a-Judge README)
CRITERIA_WEIGHTS = {
    "code_quality": 0.30,
    "efficiency": 0.25,
    "completeness": 0.25,
    "evidence": 0.20
}

# Score thresholds
SCORE_EXCELLENT = 0.90
SCORE_GOOD = 0.75
SCORE_ACCEPTABLE = 0.60
SCORE_NEEDS_WORK = 0.40


# ═══════════════════════════════════════════════════════════════════════════
# METRICS COLLECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_eval_dir() -> Path:
    """Get or create evaluation directory"""
    eval_dir = get_claude_dir() / EVAL_DIR
    ensure_dir(eval_dir)
    return eval_dir


def load_evaluation_index() -> Dict:
    """Load evaluation index"""
    index_path = get_eval_dir() / EVAL_INDEX
    content = safe_read_file(index_path, "{}")
    try:
        return json.loads(content)
    except:
        return {
            "evaluations": [],
            "statistics": {
                "total_evaluations": 0,
                "avg_score": 0.0,
                "score_distribution": {
                    "excellent": 0,
                    "good": 0,
                    "acceptable": 0,
                    "needs_work": 0,
                    "poor": 0
                }
            },
            "last_updated": get_full_timestamp()
        }


def save_evaluation_index(index: Dict) -> bool:
    """Save evaluation index"""
    index_path = get_eval_dir() / EVAL_INDEX
    index["last_updated"] = get_full_timestamp()
    return safe_write_file(index_path, json.dumps(index, indent=2, ensure_ascii=False))


def collect_session_context() -> Dict:
    """Collect context about the completed session"""
    claude_dir = get_claude_dir()

    context = {
        "timestamp": get_full_timestamp(),
        "todo_status": None,
        "handoff_content": None,
        "files_modified": [],
        "complexity_estimate": "medium"
    }

    # Check todo.md
    todo_file = claude_dir / "todo.md"
    if todo_file.exists():
        todo_content = safe_read_file(todo_file)
        context["todo_status"] = {
            "completed": len([l for l in todo_content.split('\n') if '- [x]' in l]),
            "pending": len([l for l in todo_content.split('\n') if '- [ ]' in l])
        }

    # Check HANDOFF.md
    handoff_file = claude_dir / "HANDOFF.md"
    if handoff_file.exists():
        context["handoff_content"] = safe_read_file(handoff_file)[:1000]

    # Get git status (if available)
    try:
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            cwd=get_project_dir(),
            timeout=5
        )
        if result.returncode == 0:
            context["files_modified"] = [f for f in result.stdout.strip().split('\n') if f]
    except:
        pass

    return context


# ═══════════════════════════════════════════════════════════════════════════
# EVALUATION GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_evaluation_prompt(context: Dict) -> str:
    """Generate prompt for Agent-as-a-Judge evaluation"""

    prompt = f"""# Auto-Evaluation Request

**Session Context**:
- Timestamp: {context['timestamp']}
- Files Modified: {len(context.get('files_modified', []))}
- Tasks Completed: {context.get('todo_status', {}).get('completed', 'N/A')}
- Tasks Pending: {context.get('todo_status', {}).get('pending', 'N/A')}

**Evaluation Criteria** (from Agent-as-a-Judge framework):

1. **Code Quality (30%)**:
   - SOLID principles adherence
   - DRY, KISS, YAGNI compliance
   - Code readability and maintainability

2. **Efficiency (25%)**:
   - Optimal approach used
   - Time/space complexity
   - Token efficiency

3. **Completeness (25%)**:
   - All requirements met
   - Edge cases handled
   - Error handling present

4. **Evidence (20%)**:
   - Metrics provided
   - Test results included
   - Verification performed
   - File references (file:line)

**Instructions**:
Please evaluate the completed session based on the criteria above. Provide:
- Overall Score (0.0-1.0)
- Individual criterion scores
- Strengths (2-3 points)
- Areas for Improvement (2-3 points)
- Recommendations for next session

**Context**:
{context.get('handoff_content', 'No HANDOFF.md found')}

"""

    return prompt


def parse_evaluation_response(response: str) -> Optional[Dict]:
    """Parse evaluation response and extract scores"""

    # This is a simplified parser - in production, you'd use more robust parsing
    evaluation = {
        "overall_score": 0.0,
        "criteria_scores": {
            "code_quality": 0.0,
            "efficiency": 0.0,
            "completeness": 0.0,
            "evidence": 0.0
        },
        "rating": "unknown",
        "strengths": [],
        "improvements": [],
        "recommendations": []
    }

    # Extract scores (looking for patterns like "X.XX / 1.00" or "Score: X.XX")
    import re

    overall_match = re.search(r'Overall Score[:\s]+(\d+\.?\d*)\s*/?\s*1\.?0?0?', response, re.IGNORECASE)
    if overall_match:
        evaluation["overall_score"] = float(overall_match.group(1))

    # Determine rating based on score
    score = evaluation["overall_score"]
    if score >= SCORE_EXCELLENT:
        evaluation["rating"] = "excellent"
    elif score >= SCORE_GOOD:
        evaluation["rating"] = "good"
    elif score >= SCORE_ACCEPTABLE:
        evaluation["rating"] = "acceptable"
    elif score >= SCORE_NEEDS_WORK:
        evaluation["rating"] = "needs_work"
    else:
        evaluation["rating"] = "poor"

    return evaluation


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def trigger_evaluation() -> Optional[Dict]:
    """Trigger Agent-as-a-Judge evaluation"""

    # 1. Collect session context
    context = collect_session_context()

    # 2. Check if evaluation is needed
    if not context.get('files_modified') and not context.get('todo_status'):
        return None  # No work done, skip evaluation

    # 3. Generate evaluation prompt
    prompt = generate_evaluation_prompt(context)

    # 4. Output prompt as additional context for Claude to see
    # (In a real implementation, this would trigger a separate Claude call)
    output = {
        "additionalContext": f"""
🤖 **Agent-as-a-Judge Evaluation Triggered**

The session has been completed. An automatic evaluation is recommended.

Please review the session and provide an evaluation based on:
- Code Quality (30%)
- Efficiency (25%)
- Completeness (25%)
- Evidence (20%)

Refer to `.claude/knowledge/evolution/README.md` for the evaluation template.

Session Summary:
- Files Modified: {len(context.get('files_modified', []))}
- Tasks Completed: {context.get('todo_status', {}).get('completed', 'N/A')}
"""
    }

    print(json.dumps(output, ensure_ascii=False))

    return context


def save_evaluation_result(evaluation: Dict, context: Dict) -> bool:
    """Save evaluation result to file and update index"""

    # Generate evaluation ID
    eval_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Create evaluation report
    report = f"""# Auto-Evaluation Report: {eval_id}

**Date**: {context['timestamp']}
**Overall Score**: {evaluation['overall_score']:.2f} / 1.00 ({evaluation['rating'].upper()})

---

## Session Context

- Files Modified: {len(context.get('files_modified', []))}
- Tasks Completed: {context.get('todo_status', {}).get('completed', 'N/A')}
- Tasks Pending: {context.get('todo_status', {}).get('pending', 'N/A')}

---

## Evaluation Scores

| Criterion | Weight | Score | Rating |
|-----------|--------|-------|--------|
| Code Quality | 30% | {evaluation['criteria_scores']['code_quality']:.2f} | - |
| Efficiency | 25% | {evaluation['criteria_scores']['efficiency']:.2f} | - |
| Completeness | 25% | {evaluation['criteria_scores']['completeness']:.2f} | - |
| Evidence | 20% | {evaluation['criteria_scores']['evidence']:.2f} | - |

---

## Strengths

{chr(10).join('- ' + s for s in evaluation.get('strengths', ['N/A']))}

---

## Areas for Improvement

{chr(10).join('- ' + i for i in evaluation.get('improvements', ['N/A']))}

---

## Recommendations

{chr(10).join('- ' + r for r in evaluation.get('recommendations', ['N/A']))}

---

*Generated by Agent-as-a-Judge v1.0*
*Evaluation Framework: Context Engineering Quality Standards*
"""

    # Save report
    report_path = get_eval_dir() / f"eval-{eval_id}.md"
    success = safe_write_file(report_path, report)

    if success:
        # Update index
        index = load_evaluation_index()
        index["evaluations"].append({
            "id": eval_id,
            "timestamp": context['timestamp'],
            "score": evaluation['overall_score'],
            "rating": evaluation['rating'],
            "file": str(report_path)
        })
        index["statistics"]["total_evaluations"] += 1
        index["statistics"]["score_distribution"][evaluation['rating']] += 1

        # Recalculate average
        if index["evaluations"]:
            avg = sum(e['score'] for e in index["evaluations"]) / len(index["evaluations"])
            index["statistics"]["avg_score"] = round(avg, 3)

        save_evaluation_index(index)

    return success


def main():
    """Main entry point"""
    try:
        # Trigger evaluation
        context = trigger_evaluation()

        # Note: Actual evaluation scoring would happen in a follow-up Claude interaction
        # This hook just triggers the evaluation request

    except Exception as e:
        # Silent failure - don't interrupt the session
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
