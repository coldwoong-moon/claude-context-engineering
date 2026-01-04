#!/usr/bin/env python3
"""PreToolUse:mcp__* - MCP 도구 사용 전 검증

기능:
- MCP 서버별 도구 사용 모니터링
- 민감한 작업에 대한 경고
- 알려지지 않은 MCP 서버 사용 알림
"""
import json
import sys
import re
from pathlib import Path

# utils 모듈 로드
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))


# 알려진 MCP 서버 목록 (허용됨)
KNOWN_MCP_SERVERS = {
    "context7",       # 라이브러리 문서
    "arxiv",          # 논문 검색
    "zotero",         # 문헌 관리
    "neo4j",          # 그래프 데이터베이스
    "playwright",     # 브라우저 자동화
    "browserbase",    # 클라우드 브라우저
    "chrome-tools",   # Chrome 확장
    "chrome-devtools",# Chrome DevTools
    "ide",            # IDE 통합
    "plugin_claude-mem_mem-search",  # 메모리 검색
}

# 민감한 작업 패턴 (경고만, 차단하지 않음)
SENSITIVE_PATTERNS = [
    # 브라우저 관련
    (r"mcp__playwright__browser_file_upload", "파일 업로드"),
    (r"mcp__playwright__browser_evaluate", "JavaScript 실행"),
    (r"mcp__browserbase__browserbase_stagehand_act", "브라우저 동작 실행"),

    # 데이터베이스 관련
    (r"mcp__neo4j__.*(create|update|delete)", "Neo4j 데이터 수정"),

    # 외부 서비스 인증
    (r"mcp__.*__(auth|login|credential)", "인증 관련 작업"),
]


def extract_mcp_server(tool_name: str) -> str | None:
    """MCP 도구명에서 서버명 추출

    예: mcp__context7__get-library-docs -> context7
    """
    match = re.match(r"mcp__([^_]+)__", tool_name)
    return match.group(1) if match else None


def check_sensitive(tool_name: str) -> tuple[bool, str]:
    """민감한 작업 패턴 검사"""
    for pattern, description in SENSITIVE_PATTERNS:
        if re.search(pattern, tool_name, re.IGNORECASE):
            return True, description
    return False, ""


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")

        # MCP 도구가 아니면 통과
        if not tool_name.startswith("mcp__"):
            sys.exit(0)

        # 서버명 추출
        server = extract_mcp_server(tool_name)

        contexts = []

        # 알려지지 않은 MCP 서버 경고
        if server and server not in KNOWN_MCP_SERVERS:
            contexts.append(f"ℹ️ 새 MCP 서버: {server}")

        # 민감한 작업 체크
        is_sensitive, description = check_sensitive(tool_name)
        if is_sensitive:
            contexts.append(f"⚠️ 민감 작업: {description}")

        # 컨텍스트 출력
        if contexts:
            output_context(" | ".join(contexts))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
