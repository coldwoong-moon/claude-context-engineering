#!/usr/bin/env python3
"""PostToolUse:Write - 인용 검증 알림

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-research 명령어에서 연구 문서 작성 후 인용 검증 알림
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


# 인용 패턴
CITATION_PATTERNS = [
    r'\[([A-Za-z]+\s+et\s+al\.,?\s*\d{4})\]',  # [Author et al., 2024]
    r'\(([A-Za-z]+\s+et\s+al\.,?\s*\d{4})\)',  # (Author et al., 2024)
    r'arXiv:\d+\.\d+',  # arXiv:2401.12345
    r'doi\.org/[^\s]+',  # DOI
]


def count_citations(content: str) -> int:
    """인용 수 카운트"""
    count = 0
    for pattern in CITATION_PATTERNS:
        matches = re.findall(pattern, content)
        count += len(matches)
    return count


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        # 연구 문서인지 확인
        if "research" in file_path.lower() or file_path.endswith(".md"):
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                citation_count = count_citations(content)

                if citation_count > 0:
                    output_context(f"📚 Moon Research: {citation_count}개 인용 감지됨 - 검증 권장")
                else:
                    output_context("⚠️ Moon Research: 인용 없음 - 출처 추가 권장")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
