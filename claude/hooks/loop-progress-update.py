#!/usr/bin/env python3
"""PostToolUse:Edit|Write - Moon Loop 진행 상황 업데이트

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-loop 명령어에서 파일 수정 후 진행 상황 업데이트
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_output = input_data.get("tool_output", "")
        file_path = input_data.get("tool_input", {}).get("file_path", "unknown")

        # HANDOFF.md 업데이트 확인
        handoff_path = Path(".claude/HANDOFF.md")
        if handoff_path.exists():
            # 진행 상황 추적
            output_context(f"✅ Moon Loop: 파일 수정 완료 - {Path(file_path).name}")
        else:
            output_context(f"📝 Moon Loop: {Path(file_path).name} 수정됨")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
