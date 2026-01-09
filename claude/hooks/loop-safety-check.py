#!/usr/bin/env python3
"""PreToolUse:Bash - Moon Loop 안전 검사

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-loop 명령어에서 Bash 실행 전 안전 검사
"""
import json
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import block_action, output_context
except ImportError:
    def block_action(msg): print(f"🚫 {msg}", file=sys.stderr); sys.exit(2)
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))


# 루프에서 금지된 명령 패턴
LOOP_BLOCKED_PATTERNS = [
    "git push --force",
    "git reset --hard",
    "rm -rf /",
    "drop database",
]


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        command = input_data.get("tool_input", {}).get("command", "")

        # 루프 안전 검사
        for pattern in LOOP_BLOCKED_PATTERNS:
            if pattern in command.lower():
                block_action(f"Moon Loop에서 금지된 명령: {pattern}")

        # 루프 진행 상황 로깅
        output_context("🔄 Moon Loop: Bash 명령 실행 중...")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
