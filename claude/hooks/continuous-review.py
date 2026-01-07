#!/usr/bin/env python3
"""Stop/SubagentStop - Continuous Critical Review Loop: 무중단 비판 리뷰 시스템

무중단 코드/아키텍처 리뷰를 위한 Hook:
- 리뷰 모드 활성화 시 자동 감지
- 다중 관점 순환 리뷰 (security → performance → architecture → ...)
- REVIEW_COMPLETE 신호까지 계속 진행
- 발견된 이슈 자동 추적

References:
- Boris Journey의 Verification Loop
- 3-Phase Review Framework (Critical → Feedback → Feedforward)
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

# 리뷰 완료 신호
REVIEW_COMPLETION_SIGNALS = [
    "REVIEW_COMPLETE",
    "[REVIEW_DONE]",
    "[CRITICAL_REVIEW_COMPLETE]",
    "[리뷰완료]",
    "ALL_PERSPECTIVES_REVIEWED",
]

# 리뷰 모드 활성화 키워드
REVIEW_KEYWORDS = [
    "review",
    "critique",
    "audit",
    "evaluate",
    "리뷰",
    "검토",
    "평가",
    "비판",
]

# 리뷰 관점 순서
REVIEW_PERSPECTIVES = [
    ("security", "🛡️ Security", "보안 취약점, OWASP Top 10, 인증/인가"),
    ("performance", "⚡ Performance", "시간 복잡도, 메모리 사용, 병목점"),
    ("architecture", "🏗️ Architecture", "SOLID, 의존성, 확장성"),
    ("maintainability", "🔧 Maintainability", "가독성, 테스트 용이성, 문서화"),
    ("correctness", "✅ Correctness", "로직 오류, 엣지 케이스, 버그"),
    ("best_practices", "📚 Best Practices", "컨벤션, 패턴, 안티패턴"),
]

# 상태 파일
REVIEW_STATUS_FILE = ".claude/review-status.json"
REVIEW_LOG_FILE = ".claude/review-log.md"
ISSUES_FILE = ".claude/review-issues.md"

# 기본 설정
DEFAULT_MAX_ITERATIONS = 12


# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def output_context(msg: str):
    print(json.dumps({"additionalContext": msg}, ensure_ascii=False))


def log_review(message: str):
    log_path = get_project_root() / REVIEW_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{timestamp}]\n{message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def save_issue(severity: str, category: str, description: str, file_path: str = ""):
    issues_path = get_project_root() / ISSUES_FILE
    issues_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n### [{timestamp}] {severity} - {category}\n"
    if file_path:
        entry += f"**파일**: `{file_path}`\n"
    entry += f"**설명**: {description}\n"

    with open(issues_path, "a", encoding="utf-8") as f:
        f.write(entry)


# ═══════════════════════════════════════════════════════════════════════════
# STATUS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def load_review_status() -> dict:
    status_path = get_project_root() / REVIEW_STATUS_FILE

    if not status_path.exists():
        return {
            "active": False,
            "iteration": 0,
            "maxIterations": DEFAULT_MAX_ITERATIONS,
            "target": "",  # 리뷰 대상
            "currentPerspective": 0,  # 현재 관점 인덱스
            "completedPerspectives": [],
            "issues": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "phase": "idle",  # idle, reviewing, synthesizing
            "startTime": None,
        }

    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_review_status(status: dict):
    status_path = get_project_root() / REVIEW_STATUS_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status["lastUpdated"] = datetime.now().isoformat()
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# DETECTION
# ═══════════════════════════════════════════════════════════════════════════


def has_completion_signal(text: str) -> bool:
    text_upper = text.upper()
    for signal in REVIEW_COMPLETION_SIGNALS:
        if signal.upper() in text_upper:
            return True
    return False


def is_review_mode_active(transcript: str) -> bool:
    transcript_lower = transcript.lower()
    return any(kw in transcript_lower for kw in REVIEW_KEYWORDS)


def count_issues_by_severity(transcript: str) -> dict:
    """트랜스크립트에서 이슈 심각도 카운트"""
    issues = {
        "critical": len(re.findall(r'(critical|🔴|심각)', transcript, re.IGNORECASE)),
        "high": len(re.findall(r'(high|🟠|높음)', transcript, re.IGNORECASE)),
        "medium": len(re.findall(r'(medium|🟡|중간)', transcript, re.IGNORECASE)),
        "low": len(re.findall(r'(low|🟢|낮음)', transcript, re.IGNORECASE)),
    }
    return issues


def detect_current_perspective(transcript: str) -> tuple[int, str]:
    """현재 리뷰 관점 감지"""
    transcript_lower = transcript.lower()

    for idx, (key, name, _) in enumerate(REVIEW_PERSPECTIVES):
        if key in transcript_lower or name.lower() in transcript_lower:
            return idx, key

    return 0, "security"


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION MESSAGES
# ═══════════════════════════════════════════════════════════════════════════


REVIEW_CONTINUATION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🔍 CONTINUOUS REVIEW - Iteration {iteration}/{max_iterations}   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 **리뷰 대상**: {target}                                      │
│  👁️ **현재 관점**: {current_perspective}                         │
│  📊 **진행 상황**: {completed}/{total} 관점 완료                  │
│                                                                 │
│  🐛 **발견된 이슈**:                                              │
│     🔴 Critical: {critical} | 🟠 High: {high}                    │
│     🟡 Medium: {medium}   | 🟢 Low: {low}                       │
│                                                                 │
│  📋 **다음 관점**:                                               │
│  {next_perspective}                                              │
│                                                                 │
│  💡 완료 시 REVIEW_COMPLETE 출력                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

### 현재 관점 체크리스트: {current_perspective}
{checklist}

### 리뷰 관점 진행 상황
{perspectives_status}
"""

REVIEW_COMPLETE_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🎉 CONTINUOUS REVIEW - COMPLETE!                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 **리뷰 완료**: {target}                                      │
│  📊 **총 반복**: {iteration}회                                   │
│  👁️ **검토 관점**: {perspectives_count}개                        │
│  🕐 **소요 시간**: {elapsed_time}                                │
│                                                                 │
│  🐛 **총 발견 이슈**:                                             │
│     🔴 Critical: {critical} | 🟠 High: {high}                    │
│     🟡 Medium: {medium}   | 🟢 Low: {low}                       │
│                                                                 │
│  💭 "REVIEW_COMPLETE - 다중 관점 비판 리뷰 완료!"                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""


def get_perspective_checklist(perspective_key: str) -> str:
    checklists = {
        "security": """- [ ] SQL Injection 취약점?
- [ ] XSS 취약점?
- [ ] 인증/인가 문제?
- [ ] 민감 데이터 노출?
- [ ] CSRF 보호?""",
        "performance": """- [ ] N+1 쿼리 문제?
- [ ] 불필요한 연산?
- [ ] 메모리 누수 가능성?
- [ ] 캐싱 기회?
- [ ] 비동기 처리 필요?""",
        "architecture": """- [ ] 단일 책임 원칙 준수?
- [ ] 의존성 역전 적용?
- [ ] 순환 의존성?
- [ ] 결합도/응집도?
- [ ] 확장성 고려?""",
        "maintainability": """- [ ] 코드 가독성?
- [ ] 적절한 명명?
- [ ] 충분한 주석/문서?
- [ ] 테스트 커버리지?
- [ ] 에러 핸들링?""",
        "correctness": """- [ ] 로직 오류?
- [ ] 엣지 케이스 처리?
- [ ] Null/undefined 처리?
- [ ] 타입 안전성?
- [ ] 경계 조건?""",
        "best_practices": """- [ ] 코딩 컨벤션 준수?
- [ ] 디자인 패턴 적용?
- [ ] 안티패턴 존재?
- [ ] 라이브러리 적절 사용?
- [ ] 에러 로깅?""",
    }
    return checklists.get(perspective_key, "- [ ] 검토 항목")


def get_perspectives_status(completed: list) -> str:
    lines = []
    for key, name, desc in REVIEW_PERSPECTIVES:
        status = "✅" if key in completed else "⬜"
        lines.append(f"{status} {name}: {desc}")
    return "\n".join(lines)


def format_elapsed_time(start_time_str: str) -> str:
    if not start_time_str:
        return "측정 불가"
    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = datetime.now() - start
        minutes = int(elapsed.total_seconds() // 60)
        if minutes < 60:
            return f"{minutes}분"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}시간 {mins}분"
    except Exception:
        return "측정 불가"


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")
        stop_reason = input_data.get("stop_reason", "")

        # 사용자 인터럽트 시 무시
        if stop_reason in ["user_interrupt", "max_tokens"]:
            sys.exit(0)

        # 상태 로드
        status = load_review_status()

        # 리뷰 모드가 비활성화면 무시
        if not status.get("active", False):
            if not is_review_mode_active(transcript):
                sys.exit(0)

        # 완료 신호 확인
        if has_completion_signal(transcript):
            status["active"] = False
            status["phase"] = "complete"
            save_review_status(status)
            log_review(f"Review completed: {status.get('target', 'Unknown')}")

            issues = status.get("issues", {})
            output_context(REVIEW_COMPLETE_MESSAGE.format(
                target=status.get("target", "Unknown")[:40],
                iteration=status.get("iteration", 0),
                perspectives_count=len(status.get("completedPerspectives", [])),
                elapsed_time=format_elapsed_time(status.get("startTime")),
                critical=issues.get("critical", 0),
                high=issues.get("high", 0),
                medium=issues.get("medium", 0),
                low=issues.get("low", 0),
            ))
            sys.exit(0)

        # 최대 반복 확인
        max_iterations = status.get("maxIterations", DEFAULT_MAX_ITERATIONS)
        if status.get("iteration", 0) >= max_iterations:
            status["active"] = False
            save_review_status(status)
            output_context(f"⚠️ 리뷰 최대 반복 횟수({max_iterations}) 도달.")
            sys.exit(0)

        # 이슈 카운트 업데이트
        new_issues = count_issues_by_severity(transcript)
        for severity, count in new_issues.items():
            status["issues"][severity] = status.get("issues", {}).get(severity, 0) + count

        # 현재 관점 감지 및 업데이트
        current_idx, current_key = detect_current_perspective(transcript)
        completed = status.get("completedPerspectives", [])

        if current_key not in completed:
            completed.append(current_key)
            status["completedPerspectives"] = completed

        # 다음 관점 결정
        next_idx = (current_idx + 1) % len(REVIEW_PERSPECTIVES)
        next_key, next_name, next_desc = REVIEW_PERSPECTIVES[next_idx]

        # 반복 증가
        status["iteration"] = status.get("iteration", 0) + 1
        status["currentPerspective"] = next_idx
        save_review_status(status)

        # 계속 진행 메시지
        current_name = REVIEW_PERSPECTIVES[current_idx][1]
        issues = status.get("issues", {})

        output_context(REVIEW_CONTINUATION_MESSAGE.format(
            iteration=status["iteration"],
            max_iterations=max_iterations,
            target=status.get("target", "리뷰 대상")[:30],
            current_perspective=current_name,
            completed=len(completed),
            total=len(REVIEW_PERSPECTIVES),
            critical=issues.get("critical", 0),
            high=issues.get("high", 0),
            medium=issues.get("medium", 0),
            low=issues.get("low", 0),
            next_perspective=f"{next_name}: {next_desc}",
            checklist=get_perspective_checklist(current_key),
            perspectives_status=get_perspectives_status(completed)
        ))

        log_review(f"Iteration {status['iteration']}: Perspective={current_key}")

    except Exception as e:
        log_review(f"Error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
