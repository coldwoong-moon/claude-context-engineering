#!/usr/bin/env python3
"""Stop: Ultrathink 세션 종료 - What Dent Did We Make?

"The people who are crazy enough to think they can change the world are the ones who do."

기능:
- 세션 성과 요약 (오늘의 dent)
- 다음 미완료 작업 리마인드
- Iterate Relentlessly: 개선 기회 제안
- context.md 자동 업데이트
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# ULTRATHINK: WHAT DENT DID WE MAKE?
# ═══════════════════════════════════════════════════════════════════════════

DENT_REFLECTION = """
┌─────────────────────────────────────────────────────────────┐
│  🌟 Session Reflection: What Dent Did We Make?              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  완료: {completed_count}개 작업                              │
│  미완료: {pending_count}개 작업                              │
│                                                             │
│  💭 "Did this session make our hearts sing?"                │
│                                                             │
│  🎯 다음 세션 목표: {next_task}                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""

ITERATE_SUGGESTION = """
💡 **Iterate Relentlessly**: 다음 세션을 위한 질문
   - 오늘 작성한 코드가 '미친 듯이 훌륭한가', 아니면 그냥 '작동하는가'?
   - 더 단순하게 만들 수 있는 부분은 없는가?
   - 코드베이스를 발견했을 때보다 더 나은 상태로 남겼는가?
"""


def get_pending_todos(todo_file: Path) -> list[str]:
    """미완료 작업 목록 반환"""
    if not todo_file.exists():
        return []
    content = todo_file.read_text(encoding="utf-8")
    return re.findall(r"- \[ \] (.+)", content)


def get_completed_today(todo_file: Path) -> list[str]:
    """오늘 완료된 작업 목록 반환"""
    if not todo_file.exists():
        return []
    content = todo_file.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    completed = []
    for line in content.split('\n'):
        if line.strip().startswith('- [x]') and today in line:
            match = re.match(r"- \[x\] (.+?)(?:\s*\(\d{4}-\d{2}-\d{2}\))?$", line.strip())
            if match:
                completed.append(match.group(1))
    return completed


def get_session_metrics(claude_dir: Path) -> dict:
    """세션 중 작업 메트릭 수집"""
    metrics = {
        "files_modified": 0,
        "decisions_made": 0,
    }

    # 최근 수정 파일 수 (context.md에서)
    context_file = claude_dir / "knowledge" / "context.md"
    if context_file.exists():
        content = context_file.read_text(encoding="utf-8")
        metrics["files_modified"] = content.count("- `")

    # 결정 사항 수 (decisions.md에서)
    decisions_file = claude_dir / "knowledge" / "decisions.md"
    if decisions_file.exists():
        content = decisions_file.read_text(encoding="utf-8")
        metrics["decisions_made"] = content.count("## [")

    return metrics


def update_context_file(claude_dir: Path, pending: list[str], completed: list[str]):
    """context.md에 세션 종료 기록 추가"""
    context_file = claude_dir / "knowledge" / "context.md"
    if not context_file.exists():
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    section = f"\n\n## 세션 종료 기록 ({timestamp})\n"

    if completed:
        section += f"**🌟 오늘의 dent**: {', '.join(completed[:5])}\n"

    if pending:
        section += f"**🎯 다음 목표**: {pending[0]}\n"
        if len(pending) > 1:
            section += f"**📋 대기 중**: {len(pending)-1}개 추가 작업\n"

    try:
        content = context_file.read_text(encoding="utf-8")

        # 이전 세션 종료 기록 제거 (최신 것만 유지)
        if "## 세션 종료 기록" in content:
            content = content.split("## 세션 종료 기록")[0].rstrip()

        content += section
        context_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        claude_dir = Path(project_dir) / ".claude"
        todo_file = claude_dir / "todo.md"

        if not todo_file.exists():
            sys.exit(0)

        # 미완료 및 완료 작업 조회
        pending = get_pending_todos(todo_file)
        completed = get_completed_today(todo_file)

        # context.md 업데이트
        update_context_file(claude_dir, pending, completed)

        # 세션 성과 메시지 생성
        next_task = pending[0] if pending else "새로운 목표를 설정하세요"

        reflection = DENT_REFLECTION.format(
            completed_count=len(completed),
            pending_count=len(pending),
            next_task=next_task[:40] + "..." if len(next_task) > 40 else next_task
        )

        parts = [reflection]

        # 완료 작업이 있으면 Iterate 제안
        if completed:
            parts.append(ITERATE_SUGGESTION)

        output = {
            "additionalContext": "\n".join(parts)
        }
        print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()