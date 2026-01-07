#!/usr/bin/env python3
"""Stop - Ralph Wiggum Loop: 자율적 장기 실행 작업 시스템

Ralph Wiggum 플러그인 패턴 구현:
- Stop Hook으로 세션 종료 가로채기
- 명시적 완료 신호(RALPH_COMPLETE) 감지
- todo.md 기반 작업 추적
- TDD 모드 지원
- 상태 파일로 반복 횟수 및 진행 상황 관리

References:
- https://github.com/anthropics/claude-code/tree/main/plugins
- https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops
- Boris Journey: 30일 259 PR, 40,000줄 코드 자동 생성
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# 완료 신호 목록
COMPLETION_SIGNALS = [
    "RALPH_COMPLETE",
    "[RALPH_DONE]",
    "RALPH_CANCELLED",
    "[TASK_COMPLETE]",
    "[DONE]",
    "[완료]",
    "ALL_TASKS_COMPLETE",
]

# 취소 신호
CANCEL_SIGNALS = [
    "RALPH_CANCEL",
    "RALPH_CANCELLED",
    "[CANCEL]",
    "[취소]",
]

# 상태 파일 경로
STATUS_FILE = ".claude/ralph-status.json"
TODO_FILE = ".claude/todo.md"
LOG_FILE = ".claude/ralph-loop.log"

# 기본 설정
DEFAULT_MAX_ITERATIONS = 10
DEFAULT_MAX_CONSECUTIVE_FAILURES = 3
DEFAULT_TIMEOUT_MINUTES = 60


# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def output_context(msg: str):
    """컨텍스트 메시지 출력"""
    print(json.dumps({"additionalContext": msg}, ensure_ascii=False))


def log_event(message: str):
    """로그 파일에 이벤트 기록"""
    log_path = get_project_root() / LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


# ═══════════════════════════════════════════════════════════════════════════
# STATUS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def get_status_file() -> Path:
    """상태 파일 경로 반환"""
    return get_project_root() / STATUS_FILE


def load_status() -> dict:
    """상태 파일 로드"""
    status_path = get_status_file()

    if not status_path.exists():
        return {
            "iteration": 0,
            "maxIterations": DEFAULT_MAX_ITERATIONS,
            "status": "idle",
            "currentTask": "",
            "lastTestResult": None,
            "consecutiveFailures": 0,
            "startTime": None,
            "safeWord": "RALPH_COMPLETE",
            "tddMode": False,
            "verifyCommand": None,
        }

    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return load_status.__wrapped__() if hasattr(load_status, '__wrapped__') else {}


def save_status(status: dict):
    """상태 파일 저장"""
    status_path = get_status_file()
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


def increment_iteration(status: dict) -> dict:
    """반복 횟수 증가"""
    status["iteration"] = status.get("iteration", 0) + 1
    status["lastUpdated"] = datetime.now().isoformat()
    return status


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION DETECTION
# ═══════════════════════════════════════════════════════════════════════════


def has_completion_signal(text: str, custom_safe_word: str = None) -> bool:
    """완료 신호 존재 여부 확인"""
    text_upper = text.upper()

    # 커스텀 safe word 확인
    if custom_safe_word and custom_safe_word.upper() in text_upper:
        return True

    # 기본 완료 신호 확인
    for signal in COMPLETION_SIGNALS:
        if signal.upper() in text_upper:
            return True

    return False


def has_cancel_signal(text: str) -> bool:
    """취소 신호 존재 여부 확인"""
    text_upper = text.upper()

    for signal in CANCEL_SIGNALS:
        if signal.upper() in text_upper:
            return True

    return False


def check_todo_status() -> dict:
    """todo.md에서 작업 상태 확인"""
    todo_path = get_project_root() / TODO_FILE

    result = {
        "pending": [],
        "in_progress": [],
        "completed": [],
        "blocked": [],
        "cancelled": False,
    }

    if not todo_path.exists():
        return result

    try:
        content = todo_path.read_text(encoding="utf-8")

        # 취소 신호 확인
        if has_cancel_signal(content):
            result["cancelled"] = True
            return result

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- [ ]"):
                task = line[6:].strip()
                result["pending"].append(task)
            elif line.startswith("- [x]"):
                task = line[6:].strip()
                result["completed"].append(task)
            elif line.startswith("- [~]") or line.startswith("- [>]"):
                task = line[6:].strip()
                result["in_progress"].append(task)
            elif line.startswith("- [!]"):
                task = line[6:].strip()
                if "CANCEL" in task.upper():
                    result["cancelled"] = True
                else:
                    result["blocked"].append(task)
    except Exception:
        pass

    return result


def is_all_tasks_complete(todo_status: dict) -> bool:
    """모든 작업 완료 여부 확인"""
    pending = len(todo_status["pending"])
    in_progress = len(todo_status["in_progress"])
    completed = len(todo_status["completed"])

    # 완료된 작업이 있고, 미완료 작업이 없으면 완료
    return completed > 0 and pending == 0 and in_progress == 0


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION MESSAGES
# ═══════════════════════════════════════════════════════════════════════════


CONTINUATION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🔄 RALPH LOOP - Iteration {iteration}/{max_iterations}         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📋 미완료 작업: {pending_count}개                              │
│  → {next_task}                                                  │
│                                                                 │
│  💡 완료 시 RALPH_COMPLETE 출력                                 │
│  💡 취소하려면 /cancel-ralph 실행                               │
│                                                                 │
│  ⚠️  남은 반복: {remaining} / 최대: {max_iterations}            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

COMPLETION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🎉 RALPH LOOP - COMPLETE!                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 모든 작업이 완료되었습니다!                                  │
│                                                                 │
│  📊 총 반복 횟수: {iteration}회                                 │
│  ✅ 완료된 작업: {completed_count}개                            │
│  🕐 소요 시간: {elapsed_time}                                   │
│                                                                 │
│  💭 "RALPH_COMPLETE - 릴레이 경주가 끝났습니다!"                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

CANCELLED_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  RALPH LOOP - CANCELLED                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🛑 루프가 취소되었습니다.                                       │
│                                                                 │
│  📊 완료된 반복: {iteration}회                                  │
│  ✅ 완료된 작업: {completed_count}개                            │
│  ⏸️  미완료 작업: {pending_count}개                              │
│                                                                 │
│  💡 재개하려면: /ralph-loop "작업" --resume                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

MAX_ITERATIONS_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  RALPH LOOP - MAX ITERATIONS REACHED                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🛑 최대 반복 횟수({max_iterations})에 도달했습니다.             │
│                                                                 │
│  📊 완료된 작업: {completed_count}개                            │
│  ⏸️  미완료 작업: {pending_count}개                              │
│                                                                 │
│  💡 계속하려면 --max-iterations를 늘려서 다시 실행하세요.       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""


def format_elapsed_time(start_time_str: str) -> str:
    """경과 시간 포맷"""
    if not start_time_str:
        return "측정 불가"

    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = datetime.now() - start
        minutes = int(elapsed.total_seconds() // 60)

        if minutes < 60:
            return f"{minutes}분"

        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}시간 {mins}분"
    except Exception:
        return "측정 불가"


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def main():
    try:
        # stdin에서 입력 읽기
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")
        stop_reason = input_data.get("stop_reason", "")

        # 사용자가 명시적으로 중단한 경우 무시
        if stop_reason in ["user_interrupt", "max_tokens"]:
            sys.exit(0)

        # 상태 로드
        status = load_status()

        # Ralph Loop가 활성화되지 않은 경우 (idle 상태) 무시
        if status.get("status") == "idle":
            sys.exit(0)

        # todo.md 상태 확인
        todo_status = check_todo_status()

        # 취소 신호 확인
        if todo_status["cancelled"] or has_cancel_signal(transcript):
            status["status"] = "cancelled"
            save_status(status)
            log_event("Ralph Loop cancelled by user")

            output_context(CANCELLED_MESSAGE.format(
                iteration=status.get("iteration", 0),
                completed_count=len(todo_status["completed"]),
                pending_count=len(todo_status["pending"]) + len(todo_status["in_progress"])
            ))
            sys.exit(0)

        # 완료 신호 확인
        safe_word = status.get("safeWord", "RALPH_COMPLETE")
        if has_completion_signal(transcript, safe_word) or is_all_tasks_complete(todo_status):
            status["status"] = "completed"
            save_status(status)
            log_event(f"Ralph Loop completed after {status.get('iteration', 0)} iterations")

            output_context(COMPLETION_MESSAGE.format(
                iteration=status.get("iteration", 0),
                completed_count=len(todo_status["completed"]),
                elapsed_time=format_elapsed_time(status.get("startTime"))
            ))
            sys.exit(0)

        # 최대 반복 횟수 확인
        max_iterations = status.get("maxIterations", DEFAULT_MAX_ITERATIONS)
        current_iteration = status.get("iteration", 0)

        if current_iteration >= max_iterations:
            status["status"] = "max_iterations_reached"
            save_status(status)
            log_event(f"Ralph Loop reached max iterations ({max_iterations})")

            output_context(MAX_ITERATIONS_MESSAGE.format(
                max_iterations=max_iterations,
                completed_count=len(todo_status["completed"]),
                pending_count=len(todo_status["pending"]) + len(todo_status["in_progress"])
            ))
            sys.exit(0)

        # 반복 계속 - 반복 횟수 증가
        status = increment_iteration(status)
        status["status"] = "running"
        save_status(status)

        # 다음 작업 결정
        next_task = "다음 작업을 계속 진행하세요"
        if todo_status["in_progress"]:
            next_task = todo_status["in_progress"][0]
        elif todo_status["pending"]:
            next_task = todo_status["pending"][0]

        pending_count = len(todo_status["pending"]) + len(todo_status["in_progress"])
        remaining = max_iterations - status["iteration"]

        log_event(f"Ralph Loop iteration {status['iteration']}/{max_iterations}: {next_task[:50]}")

        # 계속 진행 메시지 출력
        output_context(CONTINUATION_MESSAGE.format(
            iteration=status["iteration"],
            max_iterations=max_iterations,
            pending_count=pending_count,
            next_task=next_task[:50] + "..." if len(next_task) > 50 else next_task,
            remaining=remaining
        ))

    except Exception as e:
        log_event(f"Ralph Loop error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
