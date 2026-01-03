#!/usr/bin/env python3
"""PostToolUse:Bash - 오류 자동 기록 및 분류 (고도화 버전)

기능:
- 오류 자동 감지 및 분류 (Import, Network, Type, Runtime)
- 유사 오류 해결책 자동 추천
- knowledge/errors.md에 구조화된 형태로 기록
- 오류 패턴 학습 지원
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


# 오류 분류 규칙
ERROR_CATEGORIES = {
    "Import": [
        r"ModuleNotFoundError",
        r"ImportError",
        r"No module named",
    ],
    "Network": [
        r"ConnectionRefusedError",
        r"ConnectionError",
        r"TimeoutError",
        r"Connection refused",
        r"Network is unreachable",
    ],
    "Type": [
        r"TypeError",
        r"AttributeError",
        r"KeyError",
        r"IndexError",
    ],
    "Permission": [
        r"PermissionError",
        r"Permission denied",
        r"Access denied",
    ],
    "Syntax": [
        r"SyntaxError",
        r"IndentationError",
    ],
    "Runtime": [
        r"RuntimeError",
        r"ValueError",
        r"AssertionError",
    ],
}

# 알려진 해결책
KNOWN_SOLUTIONS = {
    "ModuleNotFoundError": "```bash\nuv sync\n```",
    "No module named": "```bash\nuv sync\n```",
    "Connection refused": "```bash\ndocker compose up -d\n```",
    "ConnectionRefusedError": "```bash\ndocker compose up -d\n```",
    "ENOENT": "파일 경로 확인 또는 디렉토리 생성",
    "Permission denied": "```bash\nchmod +x <file>\n```",
}


def classify_error(output: str) -> tuple[str, str]:
    """오류 분류 및 카테고리 반환"""
    for category, patterns in ERROR_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return category, pattern
    return "Unknown", ""


def find_solution(output: str) -> str:
    """알려진 해결책 찾기"""
    for keyword, solution in KNOWN_SOLUTIONS.items():
        if keyword.lower() in output.lower():
            return solution
    return ""


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_result = input_data.get("tool_result", {})
        stderr = tool_result.get("stderr", "")
        stdout = tool_result.get("stdout", "")
        command = input_data.get("tool_input", {}).get("command", "")

        output = stderr + stdout
        output_lower = output.lower()

        # 오류 키워드 체크
        error_keywords = ["error", "failed", "exception", "traceback", "fatal", "not found", "permission denied"]
        if not any(kw in output_lower for kw in error_keywords):
            sys.exit(0)

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        errors_file = Path(project_dir) / ".claude" / "knowledge" / "errors.md"

        if not errors_file.parent.exists():
            sys.exit(0)

        # 오류 분류
        category, pattern = classify_error(output)
        solution = find_solution(output)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        truncated_output = output[:500] + ("..." if len(output) > 500 else "")

        # 구조화된 오류 기록
        entry = f"""
## [{timestamp}] {category} Error
**패턴**: `{pattern}`
**명령어**:
```bash
{command}
```
**출력**:
```
{truncated_output}
```
"""
        if solution:
            entry += f"**추천 해결책**:\n{solution}\n"

        entry += "\n---\n"

        with open(errors_file, "a", encoding="utf-8") as f:
            f.write(entry)

        # 해결책이 있으면 컨텍스트로 주입
        if solution:
            output_msg = {
                "additionalContext": f"💡 [{category} Error] 알려진 해결책:\n{solution}"
            }
            print(json.dumps(output_msg, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()