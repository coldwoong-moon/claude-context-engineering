#!/usr/bin/env python3
"""PreToolUse:Read - 리뷰 범위 추적

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-review 명령어에서 파일 읽기 전 리뷰 범위 추적
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


# 리뷰 대상 파일 추적
_reviewed_files = set()


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        if file_path:
            path = Path(file_path)
            ext = path.suffix.lower()

            # 코드 파일 분류
            code_types = {
                ".py": "Python",
                ".ts": "TypeScript",
                ".tsx": "React/TypeScript",
                ".js": "JavaScript",
                ".jsx": "React/JavaScript",
                ".go": "Go",
                ".rs": "Rust",
                ".java": "Java",
            }

            file_type = code_types.get(ext, "Other")
            output_context(f"🔍 Moon Review: {file_type} 파일 분석 중 - {path.name}")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
