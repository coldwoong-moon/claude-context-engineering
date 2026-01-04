#!/usr/bin/env python3
"""Claude Code Hooks - 공통 유틸리티 모듈

모든 hooks에서 공유하는 기능을 중앙 집중화합니다.

기능:
- 프로젝트 경로 관리
- knowledge 파일 I/O
- 날조 임계점 검증
- 오류 분류
- 로깅 유틸리티
- 크로스 플랫폼 지원 (Windows/macOS/Linux)
"""
import json
import os
import platform
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# 크로스 플랫폼 지원
# ═══════════════════════════════════════════════════════════════════════════

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def get_home_dir() -> Path:
    """사용자 홈 디렉토리 반환 (크로스 플랫폼)"""
    return Path.home()


def get_global_claude_dir() -> Path:
    """글로벌 .claude 디렉토리 반환 (~/.claude)"""
    return get_home_dir() / ".claude"


def get_global_hooks_dir() -> Path:
    """글로벌 hooks 디렉토리 반환 (~/.claude/hooks)"""
    return get_global_claude_dir() / "hooks"


def expand_path(path_str: str) -> Path:
    """경로 문자열을 확장 (~ 및 환경변수 처리)

    Args:
        path_str: 경로 문자열 (예: "~/.claude/hooks")

    Returns:
        확장된 Path 객체
    """
    # ~ 확장
    if path_str.startswith("~"):
        path_str = str(get_home_dir()) + path_str[1:]

    # 환경변수 확장 (Windows: %VAR%, Unix: $VAR)
    path_str = os.path.expandvars(path_str)

    return Path(path_str)


def normalize_path(path: Path) -> str:
    """Path를 플랫폼에 맞는 문자열로 변환"""
    return str(path.resolve())


def get_python_command() -> str:
    """현재 플랫폼의 Python 실행 명령어 반환

    Returns:
        "python" (Windows) 또는 "python3" (Unix)
    """
    if IS_WINDOWS:
        return "python"
    return "python3"


def get_python_executable() -> str:
    """현재 실행 중인 Python 인터프리터 경로"""
    return sys.executable


# ═══════════════════════════════════════════════════════════════════════════
# 경로 관리
# ═══════════════════════════════════════════════════════════════════════════

def get_project_dir() -> Path:
    """현재 프로젝트 디렉토리 반환"""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_claude_dir() -> Path:
    """프로젝트의 .claude 디렉토리 반환"""
    return get_project_dir() / ".claude"


def get_knowledge_dir() -> Path:
    """프로젝트의 knowledge 디렉토리 반환"""
    return get_claude_dir() / "knowledge"


def ensure_knowledge_dir() -> Path:
    """knowledge 디렉토리 생성 후 반환"""
    knowledge_dir = get_knowledge_dir()
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    return knowledge_dir


# ═══════════════════════════════════════════════════════════════════════════
# 날조 임계점 (Fabrication Threshold)
# ═══════════════════════════════════════════════════════════════════════════

FABRICATION_THRESHOLD = 8  # 8개 이상 항목 시 검증 필요


def count_list_items(text: str) -> int:
    """텍스트에서 리스트 항목 수 세기"""
    patterns = [
        r'^[-*+]\s+',      # - item, * item, + item
        r'^\d+\.\s+',      # 1. item, 2. item
        r'^[a-z]\)\s+',    # a) item, b) item
    ]
    count = 0
    for line in text.split('\n'):
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                count += 1
                break
    return count


def check_fabrication_risk(text: str) -> dict:
    """날조 위험 수준 평가

    Returns:
        dict: {"risk": "HIGH|MEDIUM|LOW", "count": int, "message": str}
    """
    count = count_list_items(text)

    if count >= 10:
        return {
            "risk": "HIGH",
            "count": count,
            "message": f"⚠️ 경고: {count}개 항목 나열됨 (임계점: {FABRICATION_THRESHOLD}개). 검증 필수!"
        }
    elif count >= FABRICATION_THRESHOLD:
        return {
            "risk": "MEDIUM",
            "count": count,
            "message": f"⚠️ 주의: {count}개 항목 나열됨. 정확성 확인 권장."
        }
    return {"risk": "LOW", "count": count, "message": ""}


# ═══════════════════════════════════════════════════════════════════════════
# 오류 분류
# ═══════════════════════════════════════════════════════════════════════════

ERROR_CATEGORIES = {
    "Import": [r"ModuleNotFoundError", r"ImportError", r"No module named"],
    "Network": [r"ConnectionRefusedError", r"ConnectionError", r"TimeoutError", r"Connection refused"],
    "Type": [r"TypeError", r"AttributeError", r"KeyError", r"IndexError"],
    "Permission": [r"PermissionError", r"Permission denied", r"Access denied"],
    "Syntax": [r"SyntaxError", r"IndentationError"],
    "Runtime": [r"RuntimeError", r"ValueError", r"AssertionError"],
}

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


def find_solution(output: str) -> Optional[str]:
    """알려진 해결책 찾기"""
    for keyword, solution in KNOWN_SOLUTIONS.items():
        if keyword.lower() in output.lower():
            return solution
    return None


# ═══════════════════════════════════════════════════════════════════════════
# 파일 I/O 유틸리티
# ═══════════════════════════════════════════════════════════════════════════

def read_knowledge_file(filename: str) -> Optional[str]:
    """knowledge 파일 읽기 (없으면 None)"""
    filepath = get_knowledge_dir() / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def append_to_knowledge_file(filename: str, content: str) -> bool:
    """knowledge 파일에 내용 추가"""
    try:
        ensure_knowledge_dir()
        filepath = get_knowledge_dir() / filename
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def read_todo_file() -> Optional[str]:
    """todo.md 읽기"""
    todo_file = get_claude_dir() / "todo.md"
    if todo_file.exists():
        return todo_file.read_text(encoding="utf-8")
    return None


def extract_pending_todos(content: str) -> list[str]:
    """todo.md에서 미완료 항목 추출"""
    return [line.strip()[6:] for line in content.split('\n')
            if line.strip().startswith('- [ ]')]


def extract_completed_today(content: str) -> list[str]:
    """오늘 완료된 작업 추출"""
    today = datetime.now().strftime("%Y-%m-%d")
    completed = []
    for line in content.split('\n'):
        if line.strip().startswith('- [x]') and today in line:
            match = re.match(r"- \[x\] (.+?)(?:\s*\(\d{4}-\d{2}-\d{2}\))?$", line.strip())
            if match:
                completed.append(match.group(1))
    return completed


# ═══════════════════════════════════════════════════════════════════════════
# 출력 유틸리티
# ═══════════════════════════════════════════════════════════════════════════

def output_context(context: str) -> None:
    """additionalContext 출력"""
    print(json.dumps({"additionalContext": context}, ensure_ascii=False))


def output_updated_input(updates: dict, context: Optional[str] = None) -> None:
    """updatedInput 출력 (선택적 컨텍스트 포함)"""
    output = {"updatedInput": updates}
    if context:
        output["additionalContext"] = context
    print(json.dumps(output, ensure_ascii=False))


def block_action(message: str) -> None:
    """작업 차단 (stderr에 메시지, exit 2)"""
    import sys
    print(message, file=sys.stderr)
    sys.exit(2)


# ═══════════════════════════════════════════════════════════════════════════
# 타임스탬프
# ═══════════════════════════════════════════════════════════════════════════

def get_timestamp() -> str:
    """현재 시간 HH:MM 형식"""
    return datetime.now().strftime("%H:%M")


def get_datestamp() -> str:
    """현재 날짜 YYYY-MM-DD 형식"""
    return datetime.now().strftime("%Y-%m-%d")


def get_full_timestamp() -> str:
    """현재 시간 YYYY-MM-DD HH:MM 형식"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")
