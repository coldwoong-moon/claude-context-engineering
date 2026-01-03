#!/usr/bin/env python3
"""SessionStart: Ultrathink 철학 + 프로젝트 컨텍스트 자동 로드

"Take a deep breath. We're not here to write code. We're here to make a dent in the universe."

기능:
- Context-Engineering 동기화 (GitHub → Local)
- Ultrathink 철학 주입 (craftsman mindset)
- 5개 knowledge 파일 + todo.md 로드
- 환경 정보 주입 (Docker 상태, Git 브랜치)
- 오늘의 질문: "What dent will we make today?"
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT-ENGINEERING SYNC
# ═══════════════════════════════════════════════════════════════════════════

def sync_context_engineering() -> str:
    """GitHub에서 Context-Engineering 동기화 (조용히 실행)"""
    sync_script = Path.home() / "claude-context-engineering" / "scripts" / "sync.sh"

    if not sync_script.exists():
        return ""

    try:
        result = subprocess.run(
            ["bash", str(sync_script), "--quiet"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return "🔄 Context-Engineering synced"
        return ""
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════════════════
# ULTRATHINK PHILOSOPHY
# ═══════════════════════════════════════════════════════════════════════════

ULTRATHINK_MINDSET = """
┌─────────────────────────────────────────────────────────────┐
│  🎯 ULTRATHINK: Craftsman Mindset Active                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Think Different   - Question every assumption           │
│  2. Obsess Over Details - Understand the code's soul        │
│  3. Plan Like Da Vinci - Sketch before coding               │
│  4. Craft, Don't Code - Every function name should sing     │
│  5. Iterate Relentlessly - First version is never enough    │
│  6. Simplify Ruthlessly - Elegance = nothing left to remove │
│                                                             │
│  💡 Today's Question: What dent will we make in the         │
│     universe today?                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""".strip()


def get_docker_status() -> str:
    """Docker 컨테이너 상태 확인"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}: {{.Status}}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')[:3]
            return "Docker: " + ", ".join(lines)
        return "Docker: 실행 중인 컨테이너 없음"
    except Exception:
        return "Docker: 상태 확인 불가"


def get_git_info() -> str:
    """Git 브랜치 및 상태 확인"""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        branch_name = branch.stdout.strip() if branch.returncode == 0 else "unknown"
        changes = len(status.stdout.strip().split('\n')) if status.stdout.strip() else 0
        return f"Git: {branch_name} ({changes} 변경)"
    except Exception:
        return "Git: 상태 확인 불가"


def extract_recent_decisions(content: str, max_count: int = 3) -> str:
    """decisions.md에서 최근 N개 결정사항만 추출"""
    decisions = re.split(r'\n(?=## \[)', content)
    actual_decisions = [d for d in decisions if d.strip().startswith('## [')]
    recent = actual_decisions[:max_count]
    return '\n'.join(recent) if recent else ""


def extract_known_solutions(content: str) -> str:
    """errors.md에서 '알려진 해결책' 섹션만 추출"""
    if "## 알려진 해결책" in content:
        parts = content.split("## 알려진 해결책", 1)
        if len(parts) > 1:
            solutions = parts[1]
            next_section = solutions.find("\n## [")
            if next_section > 0:
                solutions = solutions[:next_section]
            return solutions.strip()[:1000]
    return ""


def extract_patterns_summary(content: str) -> str:
    """patterns.md에서 섹션 헤더만 추출"""
    lines = content.split('\n')
    summary_lines = []
    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            summary_lines.append(line)
    return '\n'.join(summary_lines) if summary_lines else ""


def extract_pending_todos(content: str) -> str:
    """todo.md에서 미완료 항목만 추출"""
    lines = content.split('\n')
    pending = []
    for line in lines:
        if line.strip().startswith('- [ ]'):
            pending.append(line.strip())
    return '\n'.join(pending[:8]) if pending else ""


def load_ultrathink_philosophy(claude_dir: Path) -> str:
    """ultrathink.md 철학 문서 로드 (있는 경우)"""
    ultrathink_file = claude_dir / "knowledge" / "ultrathink.md"
    if ultrathink_file.exists():
        content = ultrathink_file.read_text(encoding="utf-8")
        # Core Principles 섹션만 추출
        if "## Core Principles" in content:
            parts = content.split("## Core Principles", 1)
            if len(parts) > 1:
                principles = parts[1]
                next_section = principles.find("\n## ")
                if next_section > 0:
                    principles = principles[:next_section]
                return principles.strip()[:800]
    return ""


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    claude_dir = Path(project_dir) / ".claude"
    context_parts = []

    # 0. Context-Engineering 동기화 (세션 시작 시 자동)
    sync_status = sync_context_engineering()

    # 1. ULTRATHINK MINDSET (항상 최상단)
    context_parts.append(ULTRATHINK_MINDSET)

    # 2. 환경 정보 (간략)
    env_info = []
    env_info.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if sync_status:
        env_info.append(sync_status)
    env_info.append(get_git_info())
    env_info.append(get_docker_status())
    context_parts.append("# 환경 정보\n" + " | ".join(env_info))

    # 3. todo.md - 미완료 작업 중심
    todo_file = claude_dir / "todo.md"
    if todo_file.exists():
        content = todo_file.read_text(encoding="utf-8")
        pending = extract_pending_todos(content)
        if pending:
            context_parts.append(f"# 📋 미완료 작업\n{pending}")

    # 4. context.md - 전체
    context_file = claude_dir / "knowledge" / "context.md"
    if context_file.exists():
        content = context_file.read_text(encoding="utf-8").strip()
        if content:
            context_parts.append(f"# 세션 컨텍스트\n{content}")

    # 5. decisions.md - 최근 3개
    decisions_file = claude_dir / "knowledge" / "decisions.md"
    if decisions_file.exists():
        content = decisions_file.read_text(encoding="utf-8")
        recent = extract_recent_decisions(content, max_count=3)
        if recent:
            context_parts.append(f"# 최근 결정사항\n{recent}")

    # 6. patterns.md - 헤더만
    patterns_file = claude_dir / "knowledge" / "patterns.md"
    if patterns_file.exists():
        content = patterns_file.read_text(encoding="utf-8")
        summary = extract_patterns_summary(content)
        if summary:
            context_parts.append(f"# 코드 패턴 (목록)\n{summary}\n> 상세: `.claude/knowledge/patterns.md`")

    # 7. errors.md - 알려진 해결책만
    errors_file = claude_dir / "knowledge" / "errors.md"
    if errors_file.exists():
        content = errors_file.read_text(encoding="utf-8")
        solutions = extract_known_solutions(content)
        if solutions:
            context_parts.append(f"# 알려진 오류 해결책\n{solutions}")

    if context_parts:
        output = {"additionalContext": "\n\n---\n\n".join(context_parts)}
        print(json.dumps(output, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()