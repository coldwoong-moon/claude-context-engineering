#!/usr/bin/env python3
"""Stop/SubagentStop - Unified Agent Loop: 통합 에이전트 루프 시스템

ralph-loop, continuous-loop, continuation-enforcer를 통합한 단일 루프 시스템.

통합 대상:
- Ralph Wiggum Loop (todo.md 기반 자율 실행)
- Continuous Claude Loop (HANDOFF.md 기반 릴레이)
- Continuation Enforcer (미완료 작업 강제)

완료 신호 (통일):
- LOOP_COMPLETE, [DONE], 작업완료

References:
- Boris Journey: 30일 259 PR, 40,000줄 코드 자동 생성
- Ralph Wiggum: Stop Hook 기반 자율 루프
- Continuous Claude: HANDOFF.md 릴레이 패턴
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

# 통합 완료 신호
COMPLETION_SIGNALS = [
    "LOOP_COMPLETE",
    "[DONE]",
    "[COMPLETE]",
    "작업완료",
    "완료",
    # 레거시 지원
    "RALPH_COMPLETE",
    "CONTINUOUS_COMPLETE",
    "ALL_TASKS_COMPLETE",
]

# 취소 신호
CANCEL_SIGNALS = ["LOOP_CANCEL", "[CANCEL]", "취소", "중단"]

# 통합 상태 파일
STATE_FILE = ".claude/agent-state.json"
LOG_FILE = ".claude/loop-log.md"

# 기본 설정
DEFAULT_MAX_ITERATIONS = 15
DEFAULT_MODE = "auto"  # auto, ralph, continuous, research, review

# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def output_context(msg: str):
    print(json.dumps({"additionalContext": msg}, ensure_ascii=False))


def log_event(message: str):
    log_path = get_project_root() / LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# ═══════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT (통합)
# ═══════════════════════════════════════════════════════════════════════════


def load_state() -> dict:
    state_path = get_project_root() / STATE_FILE
    default_state = {
        "mode": "idle",  # idle, ralph, continuous, research, review
        "active": False,
        "iteration": 0,
        "maxIterations": DEFAULT_MAX_ITERATIONS,
        "startTime": None,
        "lastUpdated": None,
        # Ralph/Continuation 관련
        "todos": {"pending": [], "in_progress": [], "completed": []},
        # Continuous 관련
        "handoff": {"runNumber": 0, "nextSteps": []},
        # Research 관련
        "research": {"phase": "idle", "papersFound": 0, "papersAnalyzed": 0},
        # Review 관련
        "review": {"perspective": 0, "completedPerspectives": [], "issues": {}},
    }

    if not state_path.exists():
        return default_state

    try:
        loaded = json.loads(state_path.read_text(encoding="utf-8"))
        # 기본값 병합
        for key, value in default_state.items():
            if key not in loaded:
                loaded[key] = value
        return loaded
    except Exception:
        return default_state


def save_state(state: dict):
    state_path = get_project_root() / STATE_FILE
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state["lastUpdated"] = datetime.now().isoformat()
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# TODO PARSING (from todo.md)
# ═══════════════════════════════════════════════════════════════════════════


def parse_todo_file() -> dict:
    todo_path = get_project_root() / ".claude" / "todo.md"
    result = {"pending": [], "in_progress": [], "completed": []}

    if not todo_path.exists():
        return result

    try:
        content = todo_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- [ ]"):
                result["pending"].append(line[6:].strip())
            elif line.startswith("- [x]"):
                result["completed"].append(line[6:].strip())
            elif line.startswith("- [~]") or line.startswith("- [>]"):
                result["in_progress"].append(line[6:].strip())
    except Exception:
        pass

    return result


# ═══════════════════════════════════════════════════════════════════════════
# HANDOFF PARSING (from HANDOFF.md)
# ═══════════════════════════════════════════════════════════════════════════


def parse_handoff_file() -> dict:
    handoff_path = get_project_root() / ".claude" / "HANDOFF.md"
    result = {"runNumber": 0, "nextSteps": [], "status": ""}

    if not handoff_path.exists():
        return result

    try:
        content = handoff_path.read_text(encoding="utf-8")

        # Run 번호 추출
        match = re.search(r"\*\*Run #\*\*\s*\|\s*(\d+)", content)
        if match:
            result["runNumber"] = int(match.group(1))

        # 다음 단계 추출
        next_section = re.search(r"## Next Steps.*?\n(.*?)(?=\n##|\n---|\Z)", content, re.DOTALL)
        if next_section:
            for line in next_section.group(1).split("\n"):
                match = re.match(r"\d+\.\s+(.+)", line.strip())
                if match:
                    result["nextSteps"].append(match.group(1).strip())

        # 상태 추출
        status_match = re.search(r"\*\*상태\*\*:\s*`?(\w+)`?", content)
        if status_match:
            result["status"] = status_match.group(1).upper()

    except Exception:
        pass

    return result


# ═══════════════════════════════════════════════════════════════════════════
# DETECTION
# ═══════════════════════════════════════════════════════════════════════════


def has_completion_signal(text: str) -> bool:
    text_upper = text.upper()
    return any(signal.upper() in text_upper for signal in COMPLETION_SIGNALS)


def has_cancel_signal(text: str) -> bool:
    text_upper = text.upper()
    return any(signal.upper() in text_upper for signal in CANCEL_SIGNALS)


def detect_mode(state: dict) -> str:
    """현재 활성화된 루프 모드 감지"""
    # 명시적 모드 설정 확인
    if state.get("mode") not in ["idle", "auto"]:
        return state["mode"]

    # todo.md 존재 여부로 Ralph 모드 감지
    todos = parse_todo_file()
    if todos["pending"] or todos["in_progress"]:
        return "ralph"

    # HANDOFF.md 존재 여부로 Continuous 모드 감지
    handoff = parse_handoff_file()
    if handoff["nextSteps"]:
        return "continuous"

    return "idle"


def get_incomplete_count(todos: dict) -> int:
    return len(todos.get("pending", [])) + len(todos.get("in_progress", []))


def get_next_task(todos: dict) -> str:
    if todos.get("in_progress"):
        return todos["in_progress"][0]
    if todos.get("pending"):
        return todos["pending"][0]
    return ""


# ═══════════════════════════════════════════════════════════════════════════
# MESSAGES (경량화)
# ═══════════════════════════════════════════════════════════════════════════


def format_continuation_message(state: dict, mode: str, next_task: str) -> str:
    """경량화된 계속 진행 메시지 (50 토큰 이내)"""
    iteration = state.get("iteration", 0)
    max_iter = state.get("maxIterations", DEFAULT_MAX_ITERATIONS)
    remaining = max_iter - iteration

    if mode == "ralph":
        todos = state.get("todos", {})
        pending = get_incomplete_count(todos)
        return f"""🔄 Loop {iteration}/{max_iter} | Pending: {pending} | Next: {next_task[:40]}
💡 완료시 LOOP_COMPLETE | 취소: LOOP_CANCEL"""

    elif mode == "continuous":
        run = state.get("handoff", {}).get("runNumber", 0)
        return f"""🔄 Continuous Run #{run} | Iter: {iteration}/{max_iter}
→ {next_task[:50]}
💡 완료시 LOOP_COMPLETE"""

    else:
        return f"""🔄 Loop {iteration}/{max_iter} | {next_task[:40]}
💡 LOOP_COMPLETE로 종료"""


def format_completion_message(state: dict, mode: str) -> str:
    """경량화된 완료 메시지"""
    iteration = state.get("iteration", 0)
    elapsed = format_elapsed_time(state.get("startTime"))

    if mode == "ralph":
        completed = len(state.get("todos", {}).get("completed", []))
        return f"✅ LOOP_COMPLETE | {completed}개 작업 완료 | {iteration}회 반복 | {elapsed}"
    else:
        return f"✅ LOOP_COMPLETE | {iteration}회 반복 | {elapsed}"


def format_cancel_message(state: dict) -> str:
    """취소 메시지"""
    iteration = state.get("iteration", 0)
    return f"⏹️ Loop 취소됨 | {iteration}회 반복 완료 | 재개: 루프 다시 시작"


def format_max_iterations_message(state: dict) -> str:
    """최대 반복 도달 메시지"""
    max_iter = state.get("maxIterations", DEFAULT_MAX_ITERATIONS)
    return f"⚠️ 최대 반복({max_iter}) 도달 | 계속하려면 --max-iterations 증가"


def format_elapsed_time(start_time_str: str) -> str:
    if not start_time_str:
        return "?"
    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = datetime.now() - start
        minutes = int(elapsed.total_seconds() // 60)
        if minutes < 60:
            return f"{minutes}m"
        return f"{minutes // 60}h {minutes % 60}m"
    except Exception:
        return "?"


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")
        stop_reason = input_data.get("stop_reason", "")

        # 사용자 인터럽트 시 무시
        if stop_reason in ["user_interrupt", "max_tokens"]:
            sys.exit(0)

        # 상태 로드
        state = load_state()

        # 모드 감지
        mode = detect_mode(state)

        # 비활성 상태면 무시
        if mode == "idle" and not state.get("active", False):
            sys.exit(0)

        # 취소 신호 확인
        if has_cancel_signal(transcript):
            state["active"] = False
            state["mode"] = "idle"
            save_state(state)
            log_event(f"Loop cancelled at iteration {state.get('iteration', 0)}")
            output_context(format_cancel_message(state))
            sys.exit(0)

        # 완료 신호 확인
        if has_completion_signal(transcript):
            state["active"] = False
            state["mode"] = "idle"
            save_state(state)
            log_event(f"Loop completed at iteration {state.get('iteration', 0)}")
            output_context(format_completion_message(state, mode))
            sys.exit(0)

        # 최대 반복 확인
        max_iter = state.get("maxIterations", DEFAULT_MAX_ITERATIONS)
        if state.get("iteration", 0) >= max_iter:
            state["active"] = False
            save_state(state)
            log_event(f"Max iterations ({max_iter}) reached")
            output_context(format_max_iterations_message(state))
            sys.exit(0)

        # 모드별 상태 업데이트
        next_task = ""

        if mode == "ralph":
            todos = parse_todo_file()
            state["todos"] = todos

            # 모든 작업 완료 확인
            if get_incomplete_count(todos) == 0 and len(todos.get("completed", [])) > 0:
                state["active"] = False
                state["mode"] = "idle"
                save_state(state)
                log_event("All tasks completed")
                output_context(format_completion_message(state, mode))
                sys.exit(0)

            next_task = get_next_task(todos)

        elif mode == "continuous":
            handoff = parse_handoff_file()
            state["handoff"] = handoff

            if handoff.get("status") == "CONTINUOUS_COMPLETE":
                state["active"] = False
                state["mode"] = "idle"
                save_state(state)
                output_context(format_completion_message(state, mode))
                sys.exit(0)

            next_task = handoff["nextSteps"][0] if handoff["nextSteps"] else "HANDOFF.md 확인"

        # 반복 증가
        state["iteration"] = state.get("iteration", 0) + 1
        state["active"] = True
        state["mode"] = mode
        save_state(state)

        log_event(f"Iteration {state['iteration']}: mode={mode}, next={next_task[:30]}")

        # 계속 진행 메시지
        output_context(format_continuation_message(state, mode, next_task))

    except Exception as e:
        log_event(f"Error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
