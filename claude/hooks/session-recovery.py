#!/usr/bin/env python3
"""SessionStart: Session Recovery - 세션 복구 시스템

oh-my-opencode의 session-recovery + anthropic-context-window-limit-recovery 패턴 적용:
"Automatic recovery from failures and interruptions."

기능:
- 이전 세션 상태 복구
- 미완료 작업 자동 로드
- 중단점 복원 (checkpoint restoration)
- 오류 복구 가이드라인 주입

트리거:
- SessionStart: 세션 시작 시 자동 실행

통합:
- session-start.py와 함께 실행됨
- 복구가 필요한 경우 추가 컨텍스트 주입
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════════
# SESSION RECOVERY CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# 복구 시도 최대 기간 (시간)
RECOVERY_WINDOW_HOURS = 24

# 상태 파일명
SESSION_STATE_FILE = "session-state.json"
CHECKPOINT_FILE = "checkpoint.md"

RECOVERY_MESSAGE = """
┌─────────────────────────────────────────────────────────────┐
│  🔄 SESSION RECOVERY DETECTED                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  이전 세션이 비정상 종료되었습니다.                          │
│                                                             │
│  📋 복구된 상태:                                            │
│  - 마지막 작업: {last_task}                                 │
│  - 중단 시간: {interrupted_at}                              │
│  - 미완료 작업: {pending_count}개                           │
│                                                             │
│  💡 이전 작업을 계속하시겠습니까?                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""

CONTEXT_LIMIT_RECOVERY = """
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ CONTEXT LIMIT RECOVERY                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  이전 세션이 컨텍스트 한계로 종료되었습니다.                 │
│                                                             │
│  📌 복구 전략:                                              │
│  1. 핵심 컨텍스트만 로드됨                                  │
│  2. todo.md에서 현재 작업 상태 확인                         │
│  3. 필요시 checkpoint.md 참조                               │
│                                                             │
│  💡 권장 조치:                                              │
│  - 대화 시작 시 /compact 사용 권장                          │
│  - 긴 출력은 --uc 모드 사용                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""


# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_session_state_path(claude_dir: Path) -> Path:
    """세션 상태 파일 경로"""
    return claude_dir / "knowledge" / SESSION_STATE_FILE


def get_checkpoint_path(claude_dir: Path) -> Path:
    """체크포인트 파일 경로"""
    return claude_dir / "knowledge" / CHECKPOINT_FILE


def load_session_state(claude_dir: Path) -> dict | None:
    """이전 세션 상태 로드"""
    state_file = get_session_state_path(claude_dir)
    if not state_file.exists():
        return None

    try:
        content = state_file.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return None


def save_session_state(claude_dir: Path, state: dict):
    """현재 세션 상태 저장"""
    state_file = get_session_state_path(claude_dir)
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def clear_session_state(claude_dir: Path):
    """세션 상태 초기화 (정상 종료 시)"""
    state_file = get_session_state_path(claude_dir)
    try:
        if state_file.exists():
            state_file.unlink()
    except Exception:
        pass


def create_checkpoint(claude_dir: Path, context: str):
    """체크포인트 생성"""
    checkpoint_file = get_checkpoint_path(claude_dir)
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = f"# Checkpoint: {timestamp}\n\n{context}\n"
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


def load_checkpoint(claude_dir: Path) -> str | None:
    """체크포인트 로드"""
    checkpoint_file = get_checkpoint_path(claude_dir)
    if not checkpoint_file.exists():
        return None

    try:
        return checkpoint_file.read_text(encoding="utf-8")
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# RECOVERY DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def needs_recovery(state: dict) -> tuple[bool, str]:
    """복구 필요 여부 및 사유 판단

    Returns:
        (needs_recovery: bool, reason: str)
    """
    if not state:
        return False, ""

    # 정상 종료 여부 체크
    if state.get("clean_exit", False):
        return False, ""

    # 복구 윈도우 체크
    last_activity = state.get("last_activity")
    if last_activity:
        try:
            last_time = datetime.fromisoformat(last_activity)
            now = datetime.now()
            if now - last_time > timedelta(hours=RECOVERY_WINDOW_HOURS):
                return False, "recovery_window_expired"
        except Exception:
            pass

    # 비정상 종료 사유 확인
    exit_reason = state.get("exit_reason", "unknown")

    if exit_reason == "context_limit":
        return True, "context_limit"
    elif exit_reason == "error":
        return True, "error"
    elif exit_reason in ["interrupted", "unknown"]:
        return True, "interrupted"

    # 미완료 작업 체크
    pending_tasks = state.get("pending_tasks", 0)
    if pending_tasks > 0 and not state.get("clean_exit", False):
        return True, "incomplete_tasks"

    return False, ""


def get_pending_todos(claude_dir: Path) -> list[str]:
    """미완료 작업 목록"""
    todo_file = claude_dir / "todo.md"
    if not todo_file.exists():
        return []

    try:
        content = todo_file.read_text(encoding="utf-8")
        pending = []
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]'):
                pending.append(line.strip()[6:])
        return pending
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════
# RECOVERY CONTEXT GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_recovery_context(claude_dir: Path, state: dict, reason: str) -> str:
    """복구 컨텍스트 생성"""
    parts = []

    if reason == "context_limit":
        parts.append(CONTEXT_LIMIT_RECOVERY)
    else:
        last_task = state.get("last_task", "알 수 없음")
        interrupted_at = state.get("last_activity", "알 수 없음")
        pending = get_pending_todos(claude_dir)

        msg = RECOVERY_MESSAGE.format(
            last_task=last_task[:40] + "..." if len(last_task) > 40 else last_task,
            interrupted_at=interrupted_at,
            pending_count=len(pending)
        )
        parts.append(msg)

    # 체크포인트 로드
    checkpoint = load_checkpoint(claude_dir)
    if checkpoint:
        parts.append("\n## 📌 마지막 체크포인트")
        # 체크포인트 내용 요약 (1000자 제한)
        if len(checkpoint) > 1000:
            parts.append(checkpoint[:1000] + "\n... (생략됨)")
        else:
            parts.append(checkpoint)

    # 미완료 작업 목록
    pending = get_pending_todos(claude_dir)
    if pending:
        parts.append("\n## 📋 미완료 작업")
        for task in pending[:5]:
            parts.append(f"- [ ] {task}")
        if len(pending) > 5:
            parts.append(f"... 외 {len(pending) - 5}개")

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════

def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        claude_dir = Path(project_dir) / ".claude"

        if not claude_dir.exists():
            # 새 세션 상태 초기화
            claude_dir.mkdir(parents=True, exist_ok=True)
            save_session_state(claude_dir, {
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "clean_exit": False,
                "pending_tasks": 0,
            })
            sys.exit(0)

        # 이전 세션 상태 로드
        state = load_session_state(claude_dir)

        # 복구 필요 여부 확인
        needs, reason = needs_recovery(state)

        if needs and reason:
            # 복구 컨텍스트 생성
            recovery_context = generate_recovery_context(claude_dir, state, reason)

            output = {"additionalContext": recovery_context}
            print(json.dumps(output, ensure_ascii=False))

        # 새 세션 상태 저장 (기존 상태 초기화)
        pending = get_pending_todos(claude_dir)
        save_session_state(claude_dir, {
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "clean_exit": False,
            "pending_tasks": len(pending),
            "last_task": pending[0] if pending else "",
        })

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
