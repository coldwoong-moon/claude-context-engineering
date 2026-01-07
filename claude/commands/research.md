# /research - 체계적 문헌 연구 명령어

> 학술 논문, 기술 문서, 웹 리소스를 체계적으로 연구
> 무중단 연속 연구 모드 지원

## Quick Start

```bash
# 기본 사용
/research "LLM context engineering"

# 학술 논문 중심
/research "transformer attention" --academic

# 무중단 연속 연구
/research "RAG systems" --continuous --max-iterations 15

# BibTeX 인용 포함
/research "prompt engineering" --cite bibtex
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TOPIC` | 연구 주제 (필수) | - |
| `--academic` | 학술 논문 중심 검색 | false |
| `--web` | 웹 리소스 포함 | true |
| `--continuous` | 무중단 연속 연구 모드 | false |
| `--max-iterations N` | 최대 반복 횟수 | 15 |
| `--cite FORMAT` | 인용 형식 (bibtex, apa, mla) | bibtex |
| `--depth LEVEL` | 연구 깊이 (quick, standard, deep) | standard |
| `--years N` | 최근 N년 논문 | 5 |

## Research Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1: EXPLORATION                                           │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 키워드 추출                          │                     │
│   │ 2. 다중 소스 검색                       │                     │
│   │    • Semantic Scholar                  │                     │
│   │    • arXiv, PubMed                     │                     │
│   │    • Google Scholar                    │                     │
│   │ 3. 초기 필터링 (10-20개)               │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Phase 2: DEEP ANALYSIS                                         │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 핵심 논문 선별 (5-10개)              │                     │
│   │ 2. 상세 분석                           │                     │
│   │ 3. 인용 네트워크 탐색                  │                     │
│   │ 4. 방법론/결과 추출                    │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Phase 3: SYNTHESIS                                             │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 연구 동향 종합                      │                     │
│   │ 2. 연구 격차 식별                      │                     │
│   │ 3. 향후 연구 방향                      │                     │
│   │ 4. 인용 목록 생성                      │                     │
│   └────────────────────────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Server Usage

### Semantic Scholar
```yaml
purpose: "학술 논문 검색, DOI 조회, 인용 정보"
tools:
  - mcp__semantic_scholar__search_paper: "논문 검색"
  - mcp__semantic_scholar__get_paper: "DOI/arXiv ID로 상세 조회"
  - mcp__semantic_scholar__get_citation: "인용 형식 출력"
```

### Paper Search
```yaml
purpose: "다중 소스 검색"
tools:
  - mcp__paper_search__search_arxiv: "arXiv 검색"
  - mcp__paper_search__search_pubmed: "PubMed 검색"
  - mcp__paper_search__download_arxiv: "PDF 다운로드"
```

### Deep Research
```yaml
purpose: "웹 + 학술 통합"
tools:
  - mcp__deep_research__deep_research: "종합 연구"
```

## Source Credibility

| Tier | Source | Trust | Citation |
|------|--------|-------|----------|
| 1 | Peer-reviewed journals | 95% | 필수 |
| 2 | arXiv (>50 citations) | 80% | 필수 |
| 3 | Official docs, Tech reports | 65% | 권장 |
| 4 | Blogs, Forums | 40% | [UNVERIFIED] |

## Continuous Mode

무중단 연속 연구 모드는 `continuous-research.py` 훅과 연동:

```yaml
activation: "--continuous"

status_file: ".claude/research-status.json"
log_file: ".claude/research-log.md"
citations_file: ".claude/citations.md"

completion_signals:
  - "RESEARCH_COMPLETE"
  - "[RESEARCH_DONE]"

workflow:
  1: "Stop Hook이 완료 신호 확인"
  2: "신호 없으면 다음 검색/분석 사이클 유도"
  3: "완료 시까지 반복"
```

## Output Format

### 연구 리포트

```markdown
# Research Report: [Topic]

## Executive Summary
[핵심 발견 요약]

## Research Questions
1. [질문 1]
2. [질문 2]

## Methodology
- **Sources**: [사용 소스]
- **Keywords**: [검색 키워드]
- **Date Range**: [날짜 범위]

## Key Findings

### Finding 1: [제목]
[설명]
**Evidence**: [인용]

## Research Gaps
[연구 격차]

## References
@article{...}
```

## Examples

### 1. 빠른 조사
```bash
/research "Claude Code hooks" --depth quick
```

### 2. 심층 학술 연구
```bash
/research "Large Language Model reasoning" \
  --academic --depth deep --years 3 --cite bibtex
```

### 3. 무중단 연속 연구
```bash
/research "AI safety alignment" \
  --continuous --max-iterations 20 --academic
```

### 4. 기술 문서 중심
```bash
/research "React Server Components" --web --depth standard
```

## Delegation

연구 작업은 다음 에이전트에 위임될 수 있습니다:

| Agent | When | Purpose |
|-------|------|---------|
| `librarian` | 증거 확인 필요 | Zero Hallucination 검증 |
| `oracle` | 복잡한 분석 | 심층 분석 |
| `researcher` | 서브 주제 | 세부 연구 |

## Related

- `/critical-review` - 비판적 리뷰
- `research` 매직 키워드
- `continuous-research.py` 훅
