#!/usr/bin/env python3
"""Stop/SubagentStop - Continuous Research Loop: 무중단 문헌 연구 시스템

무중단 문헌 연구를 위한 Hook:
- 연구 모드 활성화 시 자동 감지
- 문헌 검색 → 분석 → 인용 사이클 지속
- RESEARCH_COMPLETE 신호까지 계속 진행
- 인용 체크리스트 자동 생성

References:
- Librarian Agent의 Zero Hallucination 원칙
- Systematic Literature Review 방법론
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

# 연구 완료 신호
RESEARCH_COMPLETION_SIGNALS = [
    "RESEARCH_COMPLETE",
    "[RESEARCH_DONE]",
    "[LITERATURE_COMPLETE]",
    "[연구완료]",
    "ALL_PAPERS_REVIEWED",
]

# 연구 모드 활성화 키워드
RESEARCH_KEYWORDS = [
    "research",
    "literature",
    "paper",
    "systematic review",
    "연구",
    "논문",
    "문헌",
    "리서치",
]

# 상태 파일
RESEARCH_STATUS_FILE = ".claude/research-status.json"
RESEARCH_LOG_FILE = ".claude/research-log.md"
CITATIONS_FILE = ".claude/citations.md"

# 기본 설정
DEFAULT_MAX_ITERATIONS = 15
DEFAULT_PAPERS_PER_ITERATION = 5


# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════


def get_project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def output_context(msg: str):
    print(json.dumps({"additionalContext": msg}, ensure_ascii=False))


def log_research(message: str):
    log_path = get_project_root() / RESEARCH_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{timestamp}]\n{message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


# ═══════════════════════════════════════════════════════════════════════════
# STATUS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


def load_research_status() -> dict:
    status_path = get_project_root() / RESEARCH_STATUS_FILE

    if not status_path.exists():
        return {
            "active": False,
            "iteration": 0,
            "maxIterations": DEFAULT_MAX_ITERATIONS,
            "topic": "",
            "phase": "idle",  # idle, searching, analyzing, synthesizing
            "papersFound": 0,
            "papersAnalyzed": 0,
            "citations": [],
            "gaps": [],
            "startTime": None,
        }

    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return load_research_status.__wrapped__() if hasattr(load_research_status, '__wrapped__') else {}


def save_research_status(status: dict):
    status_path = get_project_root() / RESEARCH_STATUS_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status["lastUpdated"] = datetime.now().isoformat()
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# DETECTION
# ═══════════════════════════════════════════════════════════════════════════


def has_completion_signal(text: str) -> bool:
    text_upper = text.upper()
    for signal in RESEARCH_COMPLETION_SIGNALS:
        if signal.upper() in text_upper:
            return True
    return False


def is_research_mode_active(transcript: str) -> bool:
    transcript_lower = transcript.lower()
    return any(kw in transcript_lower for kw in RESEARCH_KEYWORDS)


def detect_research_phase(transcript: str) -> str:
    """현재 연구 단계 감지"""
    transcript_lower = transcript.lower()

    if any(kw in transcript_lower for kw in ["search", "find paper", "검색", "논문 찾"]):
        return "searching"
    elif any(kw in transcript_lower for kw in ["analyze", "read", "분석", "읽"]):
        return "analyzing"
    elif any(kw in transcript_lower for kw in ["synthesize", "summary", "종합", "요약"]):
        return "synthesizing"

    return "searching"


def count_citations(transcript: str) -> int:
    """인용 수 카운트"""
    # DOI 패턴
    doi_pattern = r'10\.\d{4,}/[^\s]+'
    doi_count = len(re.findall(doi_pattern, transcript))

    # arXiv 패턴
    arxiv_pattern = r'arXiv:\d{4}\.\d{4,}'
    arxiv_count = len(re.findall(arxiv_pattern, transcript))

    # URL 패턴 (학술 사이트)
    academic_urls = len(re.findall(r'(arxiv\.org|doi\.org|scholar\.google|semanticscholar\.org)', transcript))

    return doi_count + arxiv_count + academic_urls


# ═══════════════════════════════════════════════════════════════════════════
# CONTINUATION MESSAGES
# ═══════════════════════════════════════════════════════════════════════════


RESEARCH_CONTINUATION_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  📚 CONTINUOUS RESEARCH - Iteration {iteration}/{max_iterations} │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔬 **연구 주제**: {topic}                                       │
│  📊 **현재 단계**: {phase}                                       │
│  📄 **수집 논문**: {papers_found}개                              │
│  ✅ **분석 완료**: {papers_analyzed}개                           │
│  📝 **인용 수**: {citations}개                                   │
│                                                                 │
│  📋 **다음 작업**:                                               │
│  {next_action}                                                   │
│                                                                 │
│  💡 완료 시 RESEARCH_COMPLETE 출력                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

### 연구 체크리스트
- [ ] 주요 키워드로 논문 검색 완료?
- [ ] 핵심 논문 5개 이상 분석?
- [ ] 모든 주장에 인용 포함?
- [ ] 연구 격차(gap) 식별?
- [ ] 종합 요약 작성?
"""

RESEARCH_COMPLETE_MESSAGE = """
┌─────────────────────────────────────────────────────────────────┐
│  🎉 CONTINUOUS RESEARCH - COMPLETE!                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📚 **연구 완료**: {topic}                                       │
│  📊 **총 반복**: {iteration}회                                   │
│  📄 **분석 논문**: {papers_analyzed}개                           │
│  📝 **총 인용**: {citations}개                                   │
│  🕐 **소요 시간**: {elapsed_time}                                │
│                                                                 │
│  💭 "RESEARCH_COMPLETE - 체계적 문헌 검토 완료!"                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""


def get_next_action(phase: str, status: dict) -> str:
    if phase == "searching":
        return "→ 키워드로 관련 논문 검색 계속"
    elif phase == "analyzing":
        return f"→ 논문 분석 계속 ({status.get('papersFound', 0) - status.get('papersAnalyzed', 0)}개 남음)"
    elif phase == "synthesizing":
        return "→ 연구 결과 종합 및 격차 분석"
    return "→ 연구 시작"


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
        status = load_research_status()

        # 연구 모드가 비활성화면 무시
        if not status.get("active", False):
            # 연구 키워드가 있으면 활성화 확인
            if not is_research_mode_active(transcript):
                sys.exit(0)

        # 완료 신호 확인
        if has_completion_signal(transcript):
            status["active"] = False
            status["phase"] = "complete"
            save_research_status(status)
            log_research(f"Research completed: {status.get('topic', 'Unknown')}")

            output_context(RESEARCH_COMPLETE_MESSAGE.format(
                topic=status.get("topic", "Unknown")[:40],
                iteration=status.get("iteration", 0),
                papers_analyzed=status.get("papersAnalyzed", 0),
                citations=len(status.get("citations", [])),
                elapsed_time=format_elapsed_time(status.get("startTime"))
            ))
            sys.exit(0)

        # 최대 반복 확인
        max_iterations = status.get("maxIterations", DEFAULT_MAX_ITERATIONS)
        if status.get("iteration", 0) >= max_iterations:
            status["active"] = False
            save_research_status(status)
            output_context(f"⚠️ 연구 최대 반복 횟수({max_iterations}) 도달. 계속하려면 다시 시작하세요.")
            sys.exit(0)

        # 인용 수 업데이트
        new_citations = count_citations(transcript)
        if new_citations > 0:
            status["citations"] = status.get("citations", [])
            # 실제로는 여기서 인용 추출 및 저장

        # 단계 감지
        phase = detect_research_phase(transcript)
        status["phase"] = phase

        # 반복 증가
        status["iteration"] = status.get("iteration", 0) + 1
        save_research_status(status)

        # 계속 진행 메시지
        output_context(RESEARCH_CONTINUATION_MESSAGE.format(
            iteration=status["iteration"],
            max_iterations=max_iterations,
            topic=status.get("topic", "연구 주제")[:30],
            phase=phase,
            papers_found=status.get("papersFound", 0),
            papers_analyzed=status.get("papersAnalyzed", 0),
            citations=len(status.get("citations", [])),
            next_action=get_next_action(phase, status)
        ))

        log_research(f"Iteration {status['iteration']}: Phase={phase}")

    except Exception as e:
        log_research(f"Error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
