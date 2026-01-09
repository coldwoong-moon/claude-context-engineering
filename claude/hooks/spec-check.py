#!/usr/bin/env python3
"""Spec Check Hook - Pre-Implementation Specification Enforcement

"Never code before you spec. Feature → Stories → Tasks → Atoms"

This hook triggers before major implementations to ensure
proper specification has been done first.

Triggers: PreToolUse (Write|Edit|MultiEdit) on significant changes
Output: Warning or suggestion to create spec first

Checks:
- Is there an active spec for this work?
- Has the work been atomized into tasks?
- Are dependencies mapped?
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent))
try:
    from utils import get_project_dir, get_claude_dir, safe_read_file
except ImportError:
    def get_project_dir() -> Path:
        return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

    def get_claude_dir() -> Path:
        return get_project_dir() / ".claude"

    def safe_read_file(path, default="") -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except:
            return default


# ═══════════════════════════════════════════════════════════════════════════
# SPEC CHECK CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Files that indicate an active spec
SPEC_INDICATORS = [
    "specs/requirements.md",
    "specs/design.md",
    "specs/tasks.md",
    "SPEC.md",
    "spec.md",
]

# Patterns that suggest significant implementation
SIGNIFICANT_CHANGE_PATTERNS = [
    r"^(src|lib|app)/.*\.(ts|tsx|js|jsx|py|go|rs)$",  # Source files
    r".*/(components|services|api|controllers|models)/.*",  # Architecture
    r".*/hooks/.*\.py$",  # This project's hooks
]

# Exclude patterns (trivial changes)
EXCLUDE_PATTERNS = [
    r".*\.(md|txt|json|yaml|yml)$",  # Config/docs
    r".*test.*",  # Test files
    r".*spec.*",  # Spec files
    r".*\.d\.ts$",  # Type definitions
]

SPEC_REMINDER = """
┌─────────────────────────────────────────────────────────────┐
│  💡 스펙 알림: "코드 전에 스펙"                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  스펙 없이 중요한 변경을 시작하려 합니다.                      │
│                                                             │
│  사용 권장:                                                  │
│  • 스펙: <기능> - 전체 스펙 워크플로우                        │
│  • 원자화: <작업> - 빠른 작업 분해                            │
│                                                             │
│  장점:                                                       │
│  ✓ 코딩 전 명확한 요구사항 (JSON Schema Validation 95%+)    │
│  ✓ 원자적, 테스트 가능한 작업                                │
│  ✓ 더 나은 추정 및 추적                                      │
│  ✓ 개선을 위한 진화 피드백 (Agent-as-a-Judge)               │
│  ✓ 자동 품질 평가 및 개선 제안                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""

SPEC_FOUND = """
📋 활성 스펙 발견: {spec_file}
   작업: {task_count}개 | 완료: {completed_count}개
"""


# ═══════════════════════════════════════════════════════════════════════════
# SPEC DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def find_active_spec() -> Optional[dict]:
    """Find active specification files"""
    claude_dir = get_claude_dir()

    for spec_path in SPEC_INDICATORS:
        full_path = claude_dir / spec_path
        if full_path.exists():
            content = safe_read_file(full_path)

            # Count tasks
            task_count = len(re.findall(r'TASK-\d+|^\s*[-*]\s*\[ \]', content, re.MULTILINE))
            completed_count = len(re.findall(r'^\s*[-*]\s*\[x\]', content, re.MULTILINE))

            return {
                "file": spec_path,
                "task_count": task_count,
                "completed_count": completed_count,
                "content": content[:500],  # First 500 chars
            }

    # Also check for HANDOFF.md with task structure
    handoff = claude_dir / "HANDOFF.md"
    if handoff.exists():
        content = safe_read_file(handoff)
        if "## Next Steps" in content or "## Tasks" in content:
            task_count = len(re.findall(r'^\s*\d+\.\s*\[', content, re.MULTILINE))
            return {
                "file": "HANDOFF.md",
                "task_count": task_count,
                "completed_count": 0,
                "content": content[:500],
            }

    return None


def is_significant_change(file_path: str) -> bool:
    """Determine if file change is significant (needs spec)"""
    # Check exclude patterns first
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, file_path, re.IGNORECASE):
            return False

    # Check if matches significant patterns
    for pattern in SIGNIFICANT_CHANGE_PATTERNS:
        if re.match(pattern, file_path, re.IGNORECASE):
            return True

    return False


def get_change_context() -> dict:
    """Get context about what's being changed"""
    try:
        # Read from stdin (hook input)
        input_data = json.loads(sys.stdin.read())
        tool_input = input_data.get("tool_input", {})

        file_path = tool_input.get("file_path", "")

        return {
            "file_path": file_path,
            "is_significant": is_significant_change(file_path),
        }
    except:
        return {"file_path": "", "is_significant": False}


# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════

def has_spec_reminder_been_shown() -> bool:
    """Check if spec reminder was already shown this session"""
    claude_dir = get_claude_dir()
    state_file = claude_dir / "knowledge" / ".spec-reminder-shown"

    if state_file.exists():
        try:
            timestamp = state_file.read_text().strip()
            # Check if shown within last 30 minutes
            shown_time = datetime.fromisoformat(timestamp)
            elapsed = (datetime.now() - shown_time).total_seconds()
            return elapsed < 1800  # 30 minutes
        except:
            pass

    return False


def mark_spec_reminder_shown():
    """Mark that spec reminder has been shown"""
    claude_dir = get_claude_dir()
    knowledge_dir = claude_dir / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    state_file = knowledge_dir / ".spec-reminder-shown"
    state_file.write_text(datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    try:
        context = get_change_context()

        # Only check for significant changes
        if not context["is_significant"]:
            sys.exit(0)

        # Check if spec exists
        spec = find_active_spec()

        if spec:
            # Spec found - provide status
            output = {
                "additionalContext": SPEC_FOUND.format(
                    spec_file=spec["file"],
                    task_count=spec["task_count"],
                    completed_count=spec["completed_count"]
                )
            }
            print(json.dumps(output, ensure_ascii=False))
        else:
            # No spec - show reminder (but only once per session)
            if not has_spec_reminder_been_shown():
                output = {
                    "additionalContext": SPEC_REMINDER
                }
                print(json.dumps(output, ensure_ascii=False))
                mark_spec_reminder_shown()

    except Exception:
        # Silent failure
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
