#!/usr/bin/env python3
"""PreCompact: Context Window Monitor - 컨텍스트 윈도우 사전 모니터링

oh-my-opencode의 context-window-monitor + preemptive-compaction 패턴 적용:
"Proactive context management before hitting limits."

기능:
- 컨텍스트 사용량 추정 및 경고
- 임계점 도달 전 사전 압축 권장
- 중요 컨텍스트 보존 전략 제안
- 세션 상태 스냅샷 생성

트리거:
- PreCompact: 압축 직전에 실행
- 주기적 체크 (환경변수로 제어)
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT WINDOW THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════

# Claude Opus 4.5의 컨텍스트 윈도우 기준
CONTEXT_WINDOW_LIMITS = {
    "claude-opus-4-5": 200000,
    "claude-sonnet-4": 200000,
    "claude-haiku-3-5": 200000,
    "default": 128000,
}

# 경고 임계값 (%)
THRESHOLDS = {
    "GREEN": 60,      # 60% 미만: 안전
    "YELLOW": 75,     # 60-75%: 주의
    "ORANGE": 85,     # 75-85%: 경고
    "RED": 92,        # 85-92%: 위험
    "CRITICAL": 95,   # 92-95%: 위기
}

# 상태별 메시지
STATUS_MESSAGES = {
    "GREEN": "✅ Context 안전",
    "YELLOW": "⚠️ Context 주의 - 압축 준비",
    "ORANGE": "🟠 Context 경고 - 압축 권장",
    "RED": "🔴 Context 위험 - 즉시 압축 필요",
    "CRITICAL": "🚨 Context 위기 - 긴급 압축!",
}


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT ESTIMATION
# ═══════════════════════════════════════════════════════════════════════════

def estimate_token_count(text: str) -> int:
    """텍스트 토큰 수 추정 (대략적)

    Claude 토큰 추정:
    - 영어: ~4자 = 1토큰
    - 한글: ~2자 = 1토큰 (UTF-8 특성)
    - 코드: ~3.5자 = 1토큰
    """
    if not text:
        return 0

    # 한글 비율 체크
    korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7a3'])
    total_chars = len(text)

    if korean_chars > total_chars * 0.3:
        # 한글 비중 높음
        return total_chars // 2
    else:
        # 영어/코드 비중 높음
        return total_chars // 4


def get_knowledge_files_size(claude_dir: Path) -> dict:
    """knowledge 파일들의 토큰 사용량 추정"""
    knowledge_dir = claude_dir / "knowledge"
    if not knowledge_dir.exists():
        return {}

    sizes = {}
    for file in knowledge_dir.glob("*.md"):
        try:
            content = file.read_text(encoding="utf-8")
            tokens = estimate_token_count(content)
            sizes[file.name] = tokens
        except Exception:
            pass

    return sizes


def get_context_status(usage_percent: float) -> str:
    """사용량 비율에 따른 상태 반환"""
    if usage_percent < THRESHOLDS["GREEN"]:
        return "GREEN"
    elif usage_percent < THRESHOLDS["YELLOW"]:
        return "YELLOW"
    elif usage_percent < THRESHOLDS["ORANGE"]:
        return "ORANGE"
    elif usage_percent < THRESHOLDS["RED"]:
        return "RED"
    else:
        return "CRITICAL"


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT PRESERVATION STRATEGY
# ═══════════════════════════════════════════════════════════════════════════

PRESERVATION_PRIORITIES = """
📌 **컨텍스트 보존 우선순위**:
1. 🎯 현재 진행 중인 작업 (todo.md)
2. 🏗️ 아키텍처 결정사항 (decisions.md)
3. 🔧 코드 패턴 (patterns.md 헤더)
4. ⚠️ 알려진 오류 해결책 (errors.md 요약)
5. 📝 세션 컨텍스트 핵심 (context.md 최근 항목)

❌ **제거 가능**:
- 상세 오류 로그
- 완료된 작업 기록
- 이전 세션 기록
- 중복된 파일 목록
"""

COMPACTION_SUGGESTIONS = {
    "YELLOW": [
        "불필요한 파일 탐색 결과 제거",
        "완료된 todo 항목 정리",
    ],
    "ORANGE": [
        "errors.md에서 해결된 오류 제거",
        "context.md 이전 세션 기록 정리",
        "--uc 모드 활성화 권장",
    ],
    "RED": [
        "즉시 /compact 실행",
        "핵심 컨텍스트만 유지",
        "새 세션 시작 고려",
    ],
    "CRITICAL": [
        "긴급 /compact 필수",
        "todo.md와 decisions.md만 보존",
        "새 세션 시작 강력 권장",
    ],
}


def generate_context_snapshot(claude_dir: Path, sizes: dict) -> str:
    """컨텍스트 스냅샷 생성"""
    snapshot = []
    snapshot.append("## Context Snapshot")
    snapshot.append(f"- **시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    total = sum(sizes.values())
    snapshot.append(f"- **총 토큰 추정**: ~{total:,}")

    snapshot.append("\n### 파일별 사용량:")
    for file, tokens in sorted(sizes.items(), key=lambda x: -x[1]):
        pct = (tokens / total * 100) if total > 0 else 0
        snapshot.append(f"- {file}: ~{tokens:,} ({pct:.1f}%)")

    return "\n".join(snapshot)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN MONITOR
# ═══════════════════════════════════════════════════════════════════════════

def main():
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        claude_dir = Path(project_dir) / ".claude"

        if not claude_dir.exists():
            sys.exit(0)

        # 모델 타입 확인 (환경변수)
        model = os.environ.get("CLAUDE_MODEL", "default")
        max_tokens = CONTEXT_WINDOW_LIMITS.get(model, CONTEXT_WINDOW_LIMITS["default"])

        # 현재 사용량 추정
        sizes = get_knowledge_files_size(claude_dir)
        total_tokens = sum(sizes.values())

        # CLAUDE.md 포함
        claude_md = claude_dir.parent / "CLAUDE.md"
        if claude_md.exists():
            try:
                content = claude_md.read_text(encoding="utf-8")
                sizes["CLAUDE.md"] = estimate_token_count(content)
                total_tokens += sizes["CLAUDE.md"]
            except Exception:
                pass

        # 사용량 비율 계산 (knowledge 파일만으로는 부정확하지만 참고용)
        # 실제 대화 컨텍스트는 포함되지 않음
        estimated_usage = min(total_tokens / max_tokens * 100, 100)

        # 상태 판단
        status = get_context_status(estimated_usage)
        status_msg = STATUS_MESSAGES[status]

        parts = []

        # 경고 메시지
        if status != "GREEN":
            parts.append(f"""
┌─────────────────────────────────────────────────────────────┐
│  {status_msg}
├─────────────────────────────────────────────────────────────┤
│  Knowledge 파일 추정: ~{total_tokens:,} tokens
│  (실제 대화 컨텍스트는 별도)
└─────────────────────────────────────────────────────────────┘
""")

            # 권장 조치
            suggestions = COMPACTION_SUGGESTIONS.get(status, [])
            if suggestions:
                parts.append("\n💡 **권장 조치**:")
                for s in suggestions:
                    parts.append(f"  - {s}")

            # ORANGE 이상에서 보존 우선순위 표시
            if status in ["ORANGE", "RED", "CRITICAL"]:
                parts.append(PRESERVATION_PRIORITIES)

        # 스냅샷 생성 (RED 이상에서)
        if status in ["RED", "CRITICAL"]:
            snapshot = generate_context_snapshot(claude_dir, sizes)
            snapshot_file = claude_dir / "knowledge" / "context-snapshot.md"
            try:
                snapshot_file.parent.mkdir(parents=True, exist_ok=True)
                snapshot_file.write_text(snapshot, encoding="utf-8")
                parts.append(f"\n📸 스냅샷 저장됨: {snapshot_file.name}")
            except Exception:
                pass

        if parts:
            output = {"additionalContext": "\n".join(parts)}
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
