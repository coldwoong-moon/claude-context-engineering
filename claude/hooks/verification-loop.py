#!/usr/bin/env python3
"""SubagentStop - Verification Loop: TDD 및 E2E 검증 시스템

Boris Journey 패턴 + Ralph Wiggum TDD 모드 적용:
- 서브에이전트 작업 완료 시 자동 검증 트리거
- TDD 사이클 (Red → Green → Refactor) 지원
- Playwright E2E 테스트 통합
- 결정론적 검증으로 품질 2~3배 향상

References:
- Claude Code 창시자의 7가지 기법 중 #7 검증 루프
- Ralph Wiggum TDD Mode
- Playwright E2E Testing
"""

import json
import os
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

# utils 모듈 로드
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context, check_fabrication_risk
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))
    def check_fabrication_risk(text): return {"risk": False}


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Ralph Loop 상태 파일
RALPH_STATUS_FILE = ".claude/ralph-status.json"
TEST_RESULTS_FILE = ".claude/ralph-test-results.md"

# 검증이 필요한 작업 유형
VERIFICATION_TRIGGERS = [
    (r"(created?|wrote|generated)\s+\d+\s+files?", "다수 파일 생성"),
    (r"(implemented|added|built)\s+.*(feature|function|component)", "기능 구현"),
    (r"(fixed|resolved|patched)\s+.*(bug|issue|error)", "버그 수정"),
    (r"(refactored|restructured|reorganized)", "리팩터링"),
    (r"(deleted|removed)\s+\d+\s+files?", "파일 삭제"),
    (r"(test|spec)\s+.*(added|created|wrote)", "테스트 추가"),
]

# TDD 사이클 감지 패턴
TDD_PATTERNS = {
    "red": [
        r"(wrote|created|added)\s+.*test.*fail",
        r"test.*should\s+fail",
        r"red\s+phase",
        r"failing\s+test",
    ],
    "green": [
        r"(implement|add|create).*pass\s+test",
        r"test.*pass",
        r"green\s+phase",
        r"make.*test.*pass",
    ],
    "refactor": [
        r"refactor",
        r"clean\s*up",
        r"improve.*code",
        r"remove.*duplication",
    ],
}

# 검증 체크리스트
VERIFICATION_CHECKLIST = {
    "code_change": [
        "린터/포매터 실행 완료?",
        "타입 체크 통과?",
        "기존 테스트 통과?",
    ],
    "feature": [
        "기능이 의도대로 작동?",
        "엣지 케이스 처리됨?",
        "문서 업데이트됨?",
    ],
    "bugfix": [
        "원인이 정확히 파악됨?",
        "재현 테스트 통과?",
        "회귀 테스트 추가됨?",
    ],
    "refactor": [
        "기존 동작 유지됨?",
        "성능 저하 없음?",
        "가독성 향상됨?",
    ],
    "tdd_red": [
        "테스트가 의도대로 실패?",
        "테스트가 올바른 동작을 검증?",
        "테스트 이름이 명확?",
    ],
    "tdd_green": [
        "최소한의 코드로 테스트 통과?",
        "모든 테스트 통과?",
        "기존 테스트 회귀 없음?",
    ],
    "tdd_refactor": [
        "테스트가 여전히 통과?",
        "코드 가독성 향상?",
        "중복 제거됨?",
    ],
    "e2e": [
        "모든 E2E 테스트 통과?",
        "주요 사용자 플로우 검증됨?",
        "시각적 회귀 없음?",
    ],
}

# E2E 테스트 명령어
E2E_COMMANDS = {
    "playwright": "npx playwright test",
    "cypress": "npx cypress run",
    "puppeteer": "npm run test:e2e",
}


# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def load_ralph_status() -> dict:
    """Ralph Loop 상태 로드"""
    status_path = get_project_root() / RALPH_STATUS_FILE
    if not status_path.exists():
        return {}
    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_test_result(test_type: str, passed: bool, details: str = ""):
    """테스트 결과 저장"""
    results_path = get_project_root() / TEST_RESULTS_FILE
    results_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_icon = "✅" if passed else "❌"

    entry = f"\n### [{timestamp}] {test_type}\n"
    entry += f"**결과**: {status_icon} {'PASS' if passed else 'FAIL'}\n"
    if details:
        entry += f"**상세**: {details}\n"

    if results_path.exists():
        content = results_path.read_text(encoding="utf-8")
    else:
        content = "# Ralph Loop Test Results\n\n"
        content += "> TDD 사이클 및 E2E 테스트 결과 로그\n\n---\n"

    content += entry
    results_path.write_text(content, encoding="utf-8")


def detect_e2e_framework() -> str:
    """E2E 테스트 프레임워크 감지"""
    project_root = get_project_root()

    # Playwright 확인
    if (project_root / "playwright.config.ts").exists() or \
       (project_root / "playwright.config.js").exists():
        return "playwright"

    # Cypress 확인
    if (project_root / "cypress.config.ts").exists() or \
       (project_root / "cypress.config.js").exists() or \
       (project_root / "cypress").is_dir():
        return "cypress"

    # package.json에서 확인
    pkg_json = project_root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "@playwright/test" in deps:
                return "playwright"
            if "cypress" in deps:
                return "cypress"
            if "puppeteer" in deps:
                return "puppeteer"
        except Exception:
            pass

    return ""


def run_verification_command(command: str, timeout: int = 120) -> tuple[bool, str]:
    """검증 명령 실행"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=get_project_root()
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return passed, output[:500]  # 출력 제한
    except subprocess.TimeoutExpired:
        return False, "Timeout expired"
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════
# DETECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def detect_work_type(transcript: str) -> tuple[str, str]:
    """작업 유형 감지"""
    transcript_lower = transcript.lower()

    for pattern, description in VERIFICATION_TRIGGERS:
        if re.search(pattern, transcript_lower):
            # 작업 유형 분류
            if "bug" in transcript_lower or "fix" in transcript_lower:
                return "bugfix", description
            elif "refactor" in transcript_lower:
                return "refactor", description
            elif "feature" in transcript_lower or "implement" in transcript_lower:
                return "feature", description
            elif "test" in transcript_lower:
                return "test", description
            else:
                return "code_change", description

    return "", ""


def detect_tdd_phase(transcript: str) -> str:
    """TDD 사이클 단계 감지"""
    transcript_lower = transcript.lower()

    for phase, patterns in TDD_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, transcript_lower):
                return phase

    return ""


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION MESSAGES
# ═══════════════════════════════════════════════════════════════════════════


TDD_RED_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🔴 TDD RED PHASE - 실패하는 테스트 작성됨                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 테스트가 의도대로 실패하는지 확인하세요                       │
│  → 다음 단계: 테스트를 통과시키는 최소 코드 작성 (GREEN)         │
│                                                                 │
│  ### 체크리스트                                                 │
│  {checklist}                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

TDD_GREEN_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🟢 TDD GREEN PHASE - 테스트 통과 코드 작성됨                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 모든 테스트가 통과하는지 확인하세요                          │
│  → 다음 단계: 코드 개선 (REFACTOR) 또는 다음 기능 (RED)          │
│                                                                 │
│  ### 체크리스트                                                 │
│  {checklist}                                                    │
│                                                                 │
│  {test_result}                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

TDD_REFACTOR_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🔵 TDD REFACTOR PHASE - 코드 개선 중                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 테스트가 여전히 통과하는지 확인하세요                         │
│  → 다음 단계: 새 기능 추가 (RED) 또는 완료                       │
│                                                                 │
│  ### 체크리스트                                                 │
│  {checklist}                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

E2E_VERIFICATION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🎭 E2E VERIFICATION - {framework} 테스트                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📋 검증 명령: {command}                                         │
│                                                                 │
│  ### E2E 체크리스트                                             │
│  {checklist}                                                    │
│                                                                 │
│  💡 프런트엔드 변경 시 E2E 테스트 실행 권장                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""

STANDARD_VERIFICATION_MESSAGE = """
🔍 **Verification Loop 활성화**

**감지된 작업**: {description}
**작업 유형**: {work_type}

### 검증 체크리스트
{checklist}

{fabrication_warning}

💡 검증 완료 후 [VERIFIED] 마커를 추가하세요.
"""


def format_checklist(items: list[str]) -> str:
    """체크리스트 포맷"""
    return "\n".join([f"  - [ ] {item}" for item in items])


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")

        # Ralph Loop 상태 확인 (TDD 모드 여부)
        ralph_status = load_ralph_status()
        is_tdd_mode = ralph_status.get("tddMode", False)
        verify_command = ralph_status.get("verifyCommand")

        # TDD 모드 처리
        if is_tdd_mode:
            tdd_phase = detect_tdd_phase(transcript)

            if tdd_phase == "red":
                checklist = format_checklist(VERIFICATION_CHECKLIST["tdd_red"])
                output_context(TDD_RED_MESSAGE.format(checklist=checklist))
                save_test_result("TDD Red", True, "실패하는 테스트 작성됨")
                sys.exit(0)

            elif tdd_phase == "green":
                checklist = format_checklist(VERIFICATION_CHECKLIST["tdd_green"])

                # 테스트 실행 (verify_command가 있으면)
                test_result = ""
                if verify_command:
                    passed, output = run_verification_command(verify_command)
                    test_result = f"**테스트 결과**: {'✅ PASS' if passed else '❌ FAIL'}"
                    save_test_result("TDD Green", passed, output[:100])

                output_context(TDD_GREEN_MESSAGE.format(
                    checklist=checklist,
                    test_result=test_result
                ))
                sys.exit(0)

            elif tdd_phase == "refactor":
                checklist = format_checklist(VERIFICATION_CHECKLIST["tdd_refactor"])
                output_context(TDD_REFACTOR_MESSAGE.format(checklist=checklist))
                save_test_result("TDD Refactor", True, "리팩터링 단계")
                sys.exit(0)

        # E2E 테스트 감지 및 제안
        e2e_framework = detect_e2e_framework()
        if e2e_framework and any(keyword in transcript.lower() for keyword in
                                   ["frontend", "ui", "component", "page", "button", "form"]):
            command = E2E_COMMANDS.get(e2e_framework, "npm run test:e2e")
            checklist = format_checklist(VERIFICATION_CHECKLIST["e2e"])

            output_context(E2E_VERIFICATION_MESSAGE.format(
                framework=e2e_framework.title(),
                command=command,
                checklist=checklist
            ))
            sys.exit(0)

        # 일반 작업 유형 감지
        work_type, description = detect_work_type(transcript)

        if not work_type:
            sys.exit(0)

        # Fabrication 리스크 체크
        fab_result = check_fabrication_risk(transcript)

        # 검증 체크리스트 생성
        checklist_items = VERIFICATION_CHECKLIST.get(work_type, VERIFICATION_CHECKLIST["code_change"])
        checklist_md = "\n".join([f"- [ ] {item}" for item in checklist_items])

        # Fabrication 경고 메시지
        fabrication_warning = ""
        if fab_result.get("risk"):
            fabrication_warning = f"""
⚠️ **Fabrication Risk 감지**: {fab_result.get('reason', '')}
→ 8개 이상 항목 나열 시 중간 검증 필요
"""

        # 표준 검증 메시지 출력
        output_context(STANDARD_VERIFICATION_MESSAGE.format(
            description=description,
            work_type=work_type,
            checklist=checklist_md,
            fabrication_warning=fabrication_warning
        ))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
