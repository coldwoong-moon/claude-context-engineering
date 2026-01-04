#!/usr/bin/env python3
"""PreToolUse:Edit|Write|MultiEdit - Ultrathink: Simplify Ruthlessly + 파일 보호

"Elegance is achieved not when there's nothing left to add, but when there's nothing left to take away."

기능:
- 중요 설정 파일 수정 시 경고
- 금지된 파일 수정 차단
- Simplify Ruthlessly 리마인드 (대규모 변경 시)
- 수정 이력 추적
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# ULTRATHINK: SIMPLIFY RUTHLESSLY
# ═══════════════════════════════════════════════════════════════════════════

SIMPLIFY_REMINDER = """
💡 **Simplify Ruthlessly** 체크리스트:
   - [ ] 이 변경이 정말 필요한가?
   - [ ] 더 단순한 방법은 없는가?
   - [ ] 코드베이스를 발견했을 때보다 더 나은 상태로 남기는가?
"""

# 주의가 필요한 파일 패턴 (경고만)
PROTECTED_PATTERNS = [
    "CLAUDE.md",
    "settings.json",
    "settings.local.json",
    ".env",
    ".env.local",
    ".env.production",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "docker-compose.yml",
    "Dockerfile",
    "requirements.txt",
]

# 절대 수정 금지 (exit 2)
FORBIDDEN_PATTERNS = [
    ".git/config",
    ".git/HEAD",
    ".ssh/",
    "id_rsa",
    "id_ed25519",
    "authorized_keys",
    ".gnupg/",
]

# 백업 권장 패턴
BACKUP_RECOMMENDED = [
    "CLAUDE.md",
    ".env",
    "settings.json",
]

# 대규모 변경 감지 임계값
LARGE_CHANGE_THRESHOLD = 50  # 50줄 이상 변경 시 Simplify 리마인드


def count_change_lines(tool_input: dict) -> int:
    """변경되는 줄 수 추정"""
    if "content" in tool_input:
        # Write: 전체 내용
        return tool_input["content"].count('\n')
    elif "new_string" in tool_input:
        # Edit: 새 문자열 줄 수
        return tool_input.get("new_string", "").count('\n')
    return 0


def log_edit_attempt(project_dir: str, file_path: str, action: str):
    """수정 시도 이력 기록"""
    try:
        claude_dir = Path(project_dir) / ".claude"
        log_file = claude_dir / "knowledge" / "context.md"

        if not log_file.exists():
            return

        timestamp = datetime.now().strftime("%H:%M")
        filename = Path(file_path).name

        content = log_file.read_text(encoding="utf-8")

        if "## 최근 수정" not in content:
            content += "\n\n## 최근 수정\n"

        lines = content.split('\n')
        new_lines = []
        insert_idx = None

        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == "## 최근 수정":
                insert_idx = i + 1

        if insert_idx:
            new_entry = f"- `{filename}` ({timestamp}) - {action}"
            new_lines.insert(insert_idx, new_entry)

            # 최근 수정 항목 10개로 제한
            edit_lines = [l for l in new_lines if l.startswith("- `")]
            if len(edit_lines) > 10:
                for i in range(len(new_lines) - 1, -1, -1):
                    if new_lines[i].startswith("- `") and new_lines[i] != new_entry:
                        if len([l for l in new_lines if l.startswith("- `")]) > 10:
                            new_lines.pop(i)
                            break

        log_file.write_text('\n'.join(new_lines), encoding="utf-8")

    except Exception:
        pass


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        tool_name = input_data.get("tool_name", "Edit")

        if not file_path:
            sys.exit(0)

        path = Path(file_path)
        filename = path.name
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        messages = []

        # 금지된 파일 체크
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in file_path:
                print(f"🚫 BLOCKED: 보안상 수정 금지된 파일입니다 - {pattern}", file=sys.stderr)
                sys.exit(2)

        # 수정 시도 로깅
        log_edit_attempt(project_dir, file_path, tool_name)

        # 대규모 변경 감지 → Simplify Ruthlessly 리마인드
        change_lines = count_change_lines(tool_input)
        if change_lines > LARGE_CHANGE_THRESHOLD:
            messages.append(f"📐 {change_lines}줄 변경 감지")
            messages.append(SIMPLIFY_REMINDER)

        # 보호된 파일 경고
        for pattern in PROTECTED_PATTERNS:
            if filename == pattern or file_path.endswith(pattern):
                messages.append(f"⚠️ 주의: `{filename}`은 중요한 설정 파일입니다.")
                break

        # 백업 권장
        for pattern in BACKUP_RECOMMENDED:
            if filename == pattern:
                messages.append(f"💡 팁: 수정 전 백업을 권장합니다.")
                break

        if messages:
            output = {
                "additionalContext": "\n".join(messages)
            }
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()