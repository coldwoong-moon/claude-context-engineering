#!/usr/bin/env python3
"""Stop - Ralph Loop: 명시적 완료까지 작업 지속 강제

Oh-My-OpenCode 패턴 적용:
- 명시적 완료 태그([TASK_COMPLETE])가 없으면 계속 작업 유도
- todo.md에 미완료 작업이 있으면 다음 작업 제안
- Context Rot 방지를 위한 작업 연속성 보장

참고: https://github.com/YeonGyu-Kim/oh-my-opencode
"""
import json
import sys
from pathlib import Path

# utils 모듈 로드
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context, get_project_root
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))
    def get_project_root(): return Path.cwd()


COMPLETION_MARKERS = [
    "[TASK_COMPLETE]",
    "[DONE]",
    "[완료]",
    "✅ 모든 작업 완료",
]


def check_todo_remaining() -> list[str]:
    """미완료 작업 확인"""
    project_root = get_project_root()
    todo_file = project_root / ".claude" / "todo.md"

    if not todo_file.exists():
        return []

    pending = []
    try:
        content = todo_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.strip().startswith("- [ ]"):
                task = line.replace("- [ ]", "").strip()
                if task:
                    pending.append(task)
    except Exception:
        pass

    return pending


def has_completion_marker(text: str) -> bool:
    """완료 마커 존재 여부 확인"""
    text_lower = text.lower()
    for marker in COMPLETION_MARKERS:
        if marker.lower() in text_lower:
            return True
    return False


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        stop_reason = input_data.get("stop_reason", "")
        transcript = input_data.get("transcript", "")

        # 사용자가 명시적으로 중단한 경우 무시
        if stop_reason in ["user_interrupt", "max_tokens"]:
            sys.exit(0)

        # 완료 마커가 있으면 통과
        if has_completion_marker(transcript):
            output_context("✅ [TASK_COMPLETE] 확인됨. 작업이 정상 완료되었습니다.")
            sys.exit(0)

        # 미완료 작업 확인
        pending_tasks = check_todo_remaining()

        if pending_tasks:
            next_task = pending_tasks[0]
            remaining = len(pending_tasks) - 1

            context_msg = f"""🔄 **Ralph Loop 활성화**

다음 미완료 작업이 있습니다:
→ **{next_task}**
{f'(+{remaining}개 추가 작업)' if remaining > 0 else ''}

계속 진행하시겠습니까? 완료 시 [TASK_COMPLETE] 마커를 사용하세요."""

            output_context(context_msg)
        else:
            # 완료 마커 없이 종료 시 리마인드
            output_context(
                "💡 작업이 완료되었다면 [TASK_COMPLETE] 마커를 추가해주세요. "
                "계속할 작업이 있다면 다음 단계를 진행하세요."
            )

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
