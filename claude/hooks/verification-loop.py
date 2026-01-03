#!/usr/bin/env python3
"""SubagentStop - Verification Loop: 서브에이전트 완료 시 결정론적 검증

Boris Cheny 패턴 적용:
- 서브에이전트 작업 완료 시 자동 검증 트리거
- 품질을 2~3배 높이는 검증 루프
- 결정론적 검증으로 일관성 보장

참고: Claude Code 창시자의 7가지 기법 중 #7 검증 루프
"""
import json
import sys
import re
from pathlib import Path

# utils 모듈 로드
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import output_context, check_fabrication_risk
except ImportError:
    def output_context(ctx): print(json.dumps({"additionalContext": ctx}))
    def check_fabrication_risk(text): return {"risk": False}


# 검증이 필요한 작업 유형
VERIFICATION_TRIGGERS = [
    (r"(created?|wrote|generated)\s+\d+\s+files?", "다수 파일 생성"),
    (r"(implemented|added|built)\s+.*(feature|function|component)", "기능 구현"),
    (r"(fixed|resolved|patched)\s+.*(bug|issue|error)", "버그 수정"),
    (r"(refactored|restructured|reorganized)", "리팩터링"),
    (r"(deleted|removed)\s+\d+\s+files?", "파일 삭제"),
]

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
}


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
            else:
                return "code_change", description

    return "", ""


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        transcript = input_data.get("transcript", "")

        # 작업 유형 감지
        work_type, description = detect_work_type(transcript)

        if not work_type:
            sys.exit(0)

        # Fabrication 리스크 체크
        fab_result = check_fabrication_risk(transcript)

        # 검증 체크리스트 생성
        checklist = VERIFICATION_CHECKLIST.get(work_type, VERIFICATION_CHECKLIST["code_change"])
        checklist_md = "\n".join([f"- [ ] {item}" for item in checklist])

        context_msg = f"""🔍 **Verification Loop 활성화**

**감지된 작업**: {description}
**작업 유형**: {work_type}

### 검증 체크리스트
{checklist_md}

"""

        if fab_result.get("risk"):
            context_msg += f"""
⚠️ **Fabrication Risk 감지**: {fab_result.get('reason', '')}
→ 8개 이상 항목 나열 시 중간 검증 필요
"""

        context_msg += """
💡 검증 완료 후 [VERIFIED] 마커를 추가하세요."""

        output_context(context_msg)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
