---
description: 심층 연구 모드 활성화 (학술 논문, 웹 리서치, 인용 포함)
argument-hint: <topic> [--academic] [--web] [--cite apa|bibtex|mla]
---

심층 연구 모드를 활성화하고 주어진 주제에 대해 체계적인 연구를 수행합니다.

## 연구 모드 활성화

이 명령어는 다음 리서치 도구들을 활용합니다:

### MCP 서버 (자동 활성화)
- **Semantic Scholar**: 학술 논문 검색 및 인용
- **Paper Search**: arXiv, PubMed, bioRxiv 등 다중 소스 검색
- **Deep Research**: 웹 + 학술 통합 연구

### 연구 워크플로우

```yaml
phase_1_exploration:
  - 주제 분석 및 핵심 키워드 추출
  - 초기 문헌 검색 (최근 5년 중심)
  - 관련 분야 매핑

phase_2_deep_dive:
  - 핵심 논문 심층 분석
  - 인용 네트워크 탐색 (cited by, references)
  - 방법론 및 데이터셋 파악

phase_3_synthesis:
  - 연구 동향 종합
  - 격차(gap) 및 기회 식별
  - 시각화 및 요약 생성

phase_4_documentation:
  - 구조화된 리포트 작성
  - 적절한 인용 형식 적용
  - 추가 연구 방향 제안
```

## 사용 예시

```bash
# 학술 연구 중심
/research "transformer attention mechanisms" --academic --cite bibtex

# 웹 + 학술 통합
/research "LLM agents for code generation" --web --academic

# 최신 동향 파악
/research "MCP Model Context Protocol 2025"

# 특정 분야 심층 분석
/research "retrieval augmented generation RAG" --academic --cite apa
```

## 연구 옵션

| 옵션 | 설명 |
|------|------|
| `--academic` | 학술 논문 중심 검색 (Semantic Scholar, arXiv) |
| `--web` | 웹 리소스 포함 (블로그, 문서, GitHub) |
| `--cite <format>` | 인용 형식 지정 (apa, bibtex, mla, chicago) |
| `--recent <years>` | 최근 N년 논문으로 제한 (기본: 5) |
| `--limit <n>` | 검색 결과 수 제한 (기본: 10) |

## 출력 형식

연구 결과는 다음 구조로 제공됩니다:

```markdown
# Research Report: [Topic]

## Executive Summary
[핵심 발견사항 3-5줄 요약]

## Background & Context
[연구 배경 및 현황]

## Key Findings

### 1. [Finding Category]
- **Source**: [Author et al., Year]
- **Key Insight**: [핵심 내용]
- **Methodology**: [연구 방법]

## Research Landscape
[연구 동향 시각화 또는 표]

## Gaps & Opportunities
[현재 연구의 한계 및 기회]

## Recommendations
[다음 단계 제안]

## References
[선택된 인용 형식으로 정리]
```

## 연구 품질 보장

### 소스 신뢰도 평가
- Peer-reviewed journals: ★★★★★
- Conference papers (top-tier): ★★★★☆
- arXiv preprints: ★★★☆☆
- Technical blogs: ★★☆☆☆
- General web: ★☆☆☆☆

### 인용 검증
- DOI 확인
- 저자 및 소속 검증
- 출판일 확인
- 인용 횟수 참고

## MCP 서버 요구사항

이 명령어를 최대한 활용하려면 다음 MCP 서버 설정이 권장됩니다:

```bash
# Semantic Scholar MCP 추가
claude mcp add semantic-scholar -e SEMANTIC_SCHOLAR_API_KEY="your-key" -- \
  uvx --from git+https://github.com/FujishigeTemma/semantic-scholar-mcp \
  semantic-scholar-mcp serve

# Paper Search MCP 추가
claude mcp add paper-search -- \
  uvx --from git+https://github.com/openags/paper-search-mcp \
  python -m paper_search_mcp.server

# Deep Research MCP 추가 (선택)
claude mcp add deep-research -- \
  uvx --from git+https://github.com/mcherukara/Claude-Deep-Research \
  python deep_research.py
```

## 관련 명령어

- `/research-status` - 현재 연구 진행 상황 확인
- `/cite` - 수동 인용 생성
- `/literature-review` - 문헌 리뷰 특화 모드
