#!/usr/bin/env python3
"""PostToolUse:Write - 리뷰 결과 수집

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-review 명령어에서 리뷰 문서 작성 후 결과 수집
"""
import json
import sys
import re
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))


# 심각도 패턴
SEVERITY_PATTERNS = {
    "critical": (r'🔴|CRITICAL|Critical', "critical"),
    "high": (r'🟠|HIGH|High', "high"),
    "medium": (r'🟡|MEDIUM|Medium', "medium"),
    "low": (r'🟢|LOW|Low', "low"),
}


def analyze_findings(content: str) -> dict:
    """리뷰 결과 분석"""
    findings = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for level, (pattern, key) in SEVERITY_PATTERNS.items():
        matches = re.findall(pattern, content)
        findings[key] = len(matches)

    return findings


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        # 리뷰 문서인지 확인
        if "review" in file_path.lower() or "리뷰" in file_path:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                findings = analyze_findings(content)

                total = sum(findings.values())
                if total > 0:
                    summary = f"🔴{findings['critical']} 🟠{findings['high']} 🟡{findings['medium']} 🟢{findings['low']}"
                    output_context(f"📋 Moon Review: {total}개 발견사항 - {summary}")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
