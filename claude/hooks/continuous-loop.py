#!/usr/bin/env python3
"""Stop + SubagentStop: Continuous Loop Manager

Continuous Claude 패턴 구현:
- HANDOFF.md 기반 외부 메모리 시스템
- 완료 신호(CONTINUOUS_COMPLETE) 감지
- 자동 Run 카운터 및 메트릭 업데이트
- PR Loop 모드 지원

References:
- https://anandchowdhary.com/blog/2025/running-claude-code-in-a-loop
- https://github.com/AnandChowdhary/continuous-claude
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

COMPLETION_SIGNALS = [
    "CONTINUOUS_COMPLETE",
    "CONTINUOUS_CLAUDE_PROJECT_COMPLETE",
    "[LOOP_COMPLETE]",
    "[CONTINUOUS_DONE]",
]

HANDOFF_FILE = ".claude/HANDOFF.md"
LOG_FILE = ".claude/continuous-log.md"

# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_handoff_file() -> Path:
    """HANDOFF.md 파일 경로"""
    custom = os.environ.get("CONTINUOUS_HANDOFF_FILE")
    if custom:
        return Path(custom)
    return get_project_root() / HANDOFF_FILE


def get_log_file() -> Path:
    """continuous-log.md 파일 경로"""
    return get_project_root() / LOG_FILE


def output_context(msg: str):
    """컨텍스트 메시지 출력"""
    print(json.dumps({"additionalContext": msg}, ensure_ascii=False))


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION DETECTION
# ═══════════════════════════════════════════════════════════════════════════


def has_completion_signal(text: str) -> bool:
    """완료 신호 존재 여부 확인"""
    text_upper = text.upper()
    for signal in COMPLETION_SIGNALS:
        if signal.upper() in text_upper:
            return True
    return False


def get_handoff_status(handoff_path: Path) -> str:
    """HANDOFF.md에서 현재 상태 추출"""
    if not handoff_path.exists():
        return "UNKNOWN"

    content = handoff_path.read_text(encoding="utf-8")

    # 상태 라인 찾기
    status_match = re.search(r"\*\*상태\*\*:\s*`?(\w+)`?", content)
    if status_match:
        return status_match.group(1).upper()

    # 완료 신호 확인
    if has_completion_signal(content):
        return "CONTINUOUS_COMPLETE"

    return "CONTINUING"


# ═══════════════════════════════════════════════════════════════════════════
# HANDOFF MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def parse_run_number(handoff_path: Path) -> int:
    """현재 Run 번호 추출"""
    if not handoff_path.exists():
        return 0

    content = handoff_path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Run #\*\*\s*\|\s*(\d+)", content)
    if match:
        return int(match.group(1))
    return 0


def increment_run_number(handoff_path: Path) -> int:
    """Run 번호 증가 및 업데이트"""
    if not handoff_path.exists():
        return 1

    content = handoff_path.read_text(encoding="utf-8")
    current_run = parse_run_number(handoff_path)
    new_run = current_run + 1

    # Run 번호 업데이트
    content = re.sub(
        r"(\*\*Run #\*\*\s*\|\s*)\d+",
        f"\\g<1>{new_run}",
        content
    )

    # Last Updated 업데이트
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r"(\*\*Last Updated\*\*\s*\|\s*)[^\|]+",
        f"\\g<1>{timestamp} ",
        content
    )

    handoff_path.write_text(content, encoding="utf-8")
    return new_run


def get_next_steps(handoff_path: Path) -> list[str]:
    """다음 단계 목록 추출"""
    if not handoff_path.exists():
        return []

    content = handoff_path.read_text(encoding="utf-8")

    # Next Steps 섹션 찾기
    next_section = re.search(
        r"## Next Steps.*?\n(.*?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL
    )

    if not next_section:
        return []

    steps = []
    for line in next_section.group(1).split("\n"):
        match = re.match(r"\d+\.\s+(.+)", line.strip())
        if match:
            step = match.group(1).strip()
            if step and not step.startswith("["):
                steps.append(step)

    return steps


def log_run_event(event_type: str, details: str = ""):
    """continuous-log.md에 이벤트 기록"""
    log_path = get_log_file()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    handoff_path = get_handoff_file()
    run_number = parse_run_number(handoff_path)

    entry = f"\n### [{timestamp}] Run #{run_number} - {event_type}\n"
    if details:
        entry += f"{details}\n"

    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
    else:
        content = "# Continuous Claude Log\n\n"
        content += "> 연속 실행 로그입니다.\n\n---\n"

    content += entry
    log_path.write_text(content, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION MESSAGE
# ═══════════════════════════════════════════════════════════════════════════

CONTINUATION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🔄 CONTINUOUS CLAUDE - Run #{run_number}                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📋 다음 단계:                                                  │
│  → {next_step}                                                  │
│                                                                 │
│  💡 "한 번에 하나의 의미 있는 진전만 만드세요"                   │
│                                                                 │
│  📝 HANDOFF.md를 업데이트하고 다음 실행에 바톤을 넘기세요       │
│                                                                 │
│  🏁 완료 시: 상태를 CONTINUOUS_COMPLETE로 변경하세요            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

COMPLETION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🎉 CONTINUOUS CLAUDE - COMPLETE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 모든 목표가 달성되었습니다!                                  │
│                                                                 │
│  📊 총 실행 횟수: {run_number}회                                │
│                                                                 │
│  💭 "릴레이 경주가 성공적으로 완료되었습니다"                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def main():
    try:
        # stdin에서 입력 읽기
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")
        stop_reason = input_data.get("stop_reason", "")

        # 사용자가 명시적으로 중단한 경우 무시
        if stop_reason in ["user_interrupt", "max_tokens"]:
            sys.exit(0)

        handoff_path = get_handoff_file()

        # HANDOFF.md가 없으면 Continuous Mode가 아님
        if not handoff_path.exists():
            sys.exit(0)

        # 완료 신호 확인
        status = get_handoff_status(handoff_path)

        if status == "CONTINUOUS_COMPLETE" or has_completion_signal(transcript):
            # 완료됨
            run_number = parse_run_number(handoff_path)
            log_run_event("COMPLETE", "목표 달성")

            output_context(COMPLETION_MESSAGE.format(run_number=run_number))
            sys.exit(0)

        # 계속 진행 - Run 번호 증가
        new_run = increment_run_number(handoff_path)

        # 다음 단계 확인
        next_steps = get_next_steps(handoff_path)
        next_step = next_steps[0] if next_steps else "HANDOFF.md를 확인하세요"

        # 로그 기록
        log_run_event("CONTINUE", f"다음 단계: {next_step}")

        # 계속 진행 메시지
        output_context(CONTINUATION_MESSAGE.format(
            run_number=new_run,
            next_step=next_step[:50] + "..." if len(next_step) > 50 else next_step
        ))

    except Exception as e:
        # 에러 발생 시 조용히 종료
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
