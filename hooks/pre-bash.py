#!/usr/bin/env python3
"""PreToolUse:Bash - 위험 명령 차단 (고도화 버전)

기능:
- 정규식 기반 위험 명령 차단
- 위험 수준별 분류 (CRITICAL, HIGH, MEDIUM)
- 컨텍스트 기반 경고 (차단하지 않고 주의 환기)
- updatedInput으로 안전한 명령으로 자동 변환
"""
import json
import sys
import re


# CRITICAL: 즉시 차단 (exit 2)
CRITICAL_PATTERNS = [
    (r"rm\s+-rf\s+/\s*$", "루트 디렉토리 삭제"),
    (r"rm\s+-rf\s+~", "홈 디렉토리 삭제"),
    (r"rm\s+-rf\s+\$HOME", "홈 디렉토리 삭제"),
    (r"rm\s+-rf\s+/home", "/home 디렉토리 삭제"),
    (r"rm\s+-rf\s+/Users", "/Users 디렉토리 삭제"),
    (r"mkfs\.", "파일시스템 포맷"),
    (r"dd\s+if=.*of=/dev/", "디바이스 직접 쓰기"),
    (r">\s*/dev/sd[a-z]", "디스크 디바이스 리다이렉트"),
    (r"chmod\s+-R\s+777\s+/", "루트 권한 변경"),
    (r":(){ :\|:& };:", "Fork bomb"),
]

# HIGH: 경고 후 차단 (exit 2)
HIGH_PATTERNS = [
    (r"git\s+push\s+.*--force.*main", "main 브랜치 강제 푸시"),
    (r"git\s+push\s+.*--force.*master", "master 브랜치 강제 푸시"),
    (r"git\s+reset\s+--hard\s+origin", "로컬 변경사항 전체 삭제"),
    (r"drop\s+database", "데이터베이스 삭제"),
    (r"drop\s+table", "테이블 삭제"),
]

# MEDIUM: 경고만 (차단하지 않음)
MEDIUM_PATTERNS = [
    (r"rm\s+-rf\s+\.", "현재 디렉토리 삭제"),
    (r"git\s+push\s+--force", "강제 푸시"),
    (r"npm\s+publish", "패키지 배포"),
    (r"pip\s+install\s+--upgrade", "패키지 업그레이드"),
]

# 안전한 버전으로 자동 변환
SAFE_TRANSFORMS = {
    r"rm\s+-rf\s+([^/~\$].+)": lambda m: f"rm -rf ./{m.group(1)}" if not m.group(1).startswith('./') else None,
}


def check_patterns(command: str, patterns: list, level: str) -> tuple[bool, str]:
    """패턴 매칭 검사"""
    for pattern, description in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"[{level}] {description}"
    return False, ""


def try_safe_transform(command: str) -> str | None:
    """안전한 명령으로 변환 시도"""
    for pattern, transform in SAFE_TRANSFORMS.items():
        match = re.search(pattern, command)
        if match:
            result = transform(match)
            if result:
                return result
    return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        command = input_data.get("tool_input", {}).get("command", "")

        # CRITICAL 패턴 체크 - 즉시 차단
        matched, msg = check_patterns(command, CRITICAL_PATTERNS, "CRITICAL")
        if matched:
            print(f"🚫 BLOCKED: {msg}", file=sys.stderr)
            sys.exit(2)

        # HIGH 패턴 체크 - 경고 후 차단
        matched, msg = check_patterns(command, HIGH_PATTERNS, "HIGH")
        if matched:
            print(f"⛔ BLOCKED: {msg}", file=sys.stderr)
            sys.exit(2)

        # MEDIUM 패턴 체크 - 경고만 (차단하지 않음)
        matched, msg = check_patterns(command, MEDIUM_PATTERNS, "MEDIUM")
        if matched:
            output = {
                "additionalContext": f"⚠️ 주의: {msg}. 실행 전 확인이 필요합니다."
            }
            print(json.dumps(output, ensure_ascii=False))
            sys.exit(0)

        # 안전한 명령으로 변환 시도
        safe_command = try_safe_transform(command)
        if safe_command:
            output = {
                "updatedInput": {"command": safe_command},
                "additionalContext": f"✅ 안전 모드: '{command}' → '{safe_command}'로 변환됨"
            }
            print(json.dumps(output, ensure_ascii=False))
            sys.exit(0)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()