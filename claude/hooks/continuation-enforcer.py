#!/usr/bin/env python3
"""SubagentStop + Stop: Continuation Enforcer - 작업 완료 강제 시스템

oh-my-opencode의 todo-continuation-enforcer 패턴 적용:
"Work, delegate, verify, ship. No AI slop."

기능:
- 미완료 작업 감지 시 자동 리마인드
- 조기 중단 방지 (premature stopping prevention)
- 컨텍스트 주입으로 작업 연속성 유지
- Sisyphus 철학: 명시적 완료 요청 전까지 계속 진행

통합 대상 Hook Events:
- SubagentStop: 서브에이전트 종료 시 미완료 작업 체크
- Stop: 메인 세션 종료 시 미완료 작업 경고
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION ENFORCER PHILOSOPHY
# ═══════════════════════════════════════════════════════════════════════════

CONTINUATION_REMINDER = """
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  CONTINUATION ENFORCER: 미완료 작업 감지됨              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎯 "Never stop until explicitly asked."                    │
│                                                             │
│  미완료 작업이 {pending_count}개 남아있습니다.              │
│  다음 작업을 계속 진행하세요:                               │
│                                                             │
│  → {next_task}                                              │
│                                                             │
│  💡 작업을 중단하려면 사용자의 명시적 요청이 필요합니다.    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""

COMPLETION_CELEBRATION = """
┌─────────────────────────────────────────────────────────────┐
│  🎉 ALL TASKS COMPLETED                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  모든 작업이 완료되었습니다!                                 │
│                                                             │
│  ✅ 완료: {completed_count}개 작업                          │
│  🕐 소요: {elapsed_time}                                     │
│                                                             │
│  💭 "Did this session make our hearts sing?"                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""


# ═══════════════════════════════════════════════════════════════════════════
# TASK STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_todo_file(claude_dir: Path) -> Path:
    """todo.md 파일 경로 반환"""
    return claude_dir / "todo.md"


def parse_todos(content: str) -> dict:
    """todo.md 파싱 - 상태별 분류"""
    result = {
        "pending": [],
        "in_progress": [],
        "completed": [],
        "blocked": []
    }

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- [ ]'):
            # Pending task
            task = line[6:].strip()
            result["pending"].append(task)
        elif line.startswith('- [x]'):
            # Completed task
            task = line[6:].strip()
            result["completed"].append(task)
        elif line.startswith('- [~]') or line.startswith('- [>]'):
            # In progress (다양한 마커 지원)
            task = line[6:].strip()
            result["in_progress"].append(task)
        elif line.startswith('- [!]') or line.startswith('- [b]'):
            # Blocked
            task = line[6:].strip()
            result["blocked"].append(task)

    return result


def get_incomplete_count(todos: dict) -> int:
    """미완료 작업 수"""
    return len(todos["pending"]) + len(todos["in_progress"])


def get_next_task(todos: dict) -> str:
    """다음 작업 반환 (in_progress 우선)"""
    if todos["in_progress"]:
        return todos["in_progress"][0]
    if todos["pending"]:
        return todos["pending"][0]
    return "모든 작업 완료!"


def get_session_start_time(claude_dir: Path) -> datetime:
    """세션 시작 시간 추정 (context.md 기준)"""
    context_file = claude_dir / "knowledge" / "context.md"
    if context_file.exists():
        # 파일 수정 시간을 세션 시작 시간으로 사용
        return datetime.fromtimestamp(context_file.stat().st_mtime)
    return datetime.now()


def format_elapsed_time(start: datetime) -> str:
    """경과 시간 포맷"""
    elapsed = datetime.now() - start
    minutes = int(elapsed.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes}분"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}시간 {mins}분"


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def should_enforce_continuation(todos: dict, event_type: str) -> bool:
    """연속 작업 강제 여부 판단

    조건:
    1. 미완료 작업이 있음
    2. SubagentStop 또는 Stop 이벤트
    3. 강제 중단 플래그가 없음
    """
    incomplete = get_incomplete_count(todos)

    # 완료된 경우 강제하지 않음
    if incomplete == 0:
        return False

    # 미완료 작업이 있으면 강제
    return True


def record_continuation_event(claude_dir: Path, todos: dict, event_type: str):
    """연속 작업 이벤트 기록"""
    log_file = claude_dir / "knowledge" / "context.md"
    if not log_file.exists():
        return

    try:
        timestamp = datetime.now().strftime("%H:%M")
        incomplete = get_incomplete_count(todos)
        next_task = get_next_task(todos)

        entry = f"\n### Continuation Event ({timestamp})\n"
        entry += f"- **Event**: {event_type}\n"
        entry += f"- **미완료**: {incomplete}개\n"
        entry += f"- **다음 작업**: {next_task[:50]}...\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════

def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        claude_dir = Path(project_dir) / ".claude"
        todo_file = get_todo_file(claude_dir)

        # Hook 이벤트 타입 감지 (환경변수 또는 stdin)
        event_type = os.environ.get("CLAUDE_HOOK_EVENT", "Stop")

        if not todo_file.exists():
            sys.exit(0)

        content = todo_file.read_text(encoding="utf-8")
        todos = parse_todos(content)

        incomplete = get_incomplete_count(todos)

        if incomplete > 0:
            # 미완료 작업 존재 → 연속 작업 강제
            next_task = get_next_task(todos)

            reminder = CONTINUATION_REMINDER.format(
                pending_count=incomplete,
                next_task=next_task[:60] + "..." if len(next_task) > 60 else next_task
            )

            # 이벤트 기록
            record_continuation_event(claude_dir, todos, event_type)

            output = {"additionalContext": reminder}
            print(json.dumps(output, ensure_ascii=False))
        else:
            # 모든 작업 완료
            start_time = get_session_start_time(claude_dir)
            elapsed = format_elapsed_time(start_time)

            celebration = COMPLETION_CELEBRATION.format(
                completed_count=len(todos["completed"]),
                elapsed_time=elapsed
            )

            output = {"additionalContext": celebration}
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
