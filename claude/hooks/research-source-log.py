#!/usr/bin/env python3
"""PreToolUse:WebSearch|WebFetch - 연구 소스 로깅

Claude Code 2.1+ Agent Hooks in Frontmatter 기능 활용
/moon-research 명령어에서 웹 검색/페치 전 소스 로깅
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


def log_source(source_type: str, query_or_url: str):
    """연구 소스 로깅"""
    log_path = Path(".claude/knowledge/research/search-log.md")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    entry = f"- [{timestamp}] {source_type}: {query_or_url}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name == "WebSearch":
            query = tool_input.get("query", "")
            log_source("WebSearch", query)
            output_context(f"🔍 Moon Research: 웹 검색 - \"{query}\"")

        elif tool_name == "WebFetch":
            url = tool_input.get("url", "")
            log_source("WebFetch", url)
            output_context(f"🌐 Moon Research: 페이지 가져오기 - {url}")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
