# Research Skill - 체계적 문헌 연구

> 학술 논문, 기술 문서, 웹 리소스를 체계적으로 연구하는 스킬
> 무중단 연구 모드 지원 (continuous-research.py 훅 연동)

## Activation

```bash
# 매직 키워드로 활성화
research <topic>
연구 <주제>
/research <topic>

# 명령어로 활성화
/research "LLM context engineering" --academic --continuous
```

## Core Workflow

```yaml
phase_1_exploration:
  name: "탐색 단계"
  actions:
    - 키워드 추출 및 검색 쿼리 생성
    - 다중 소스 검색 (arXiv, Semantic Scholar, Google Scholar)
    - 관련성 기반 필터링
  output:
    - 초기 논문 목록 (10-20개)
    - 키워드 맵

phase_2_deep_analysis:
  name: "심층 분석 단계"
  actions:
    - 핵심 논문 선별 (Top 5-10)
    - 논문별 상세 분석
    - 인용 네트워크 탐색
    - 방법론 및 결과 추출
  output:
    - 논문별 분석 노트
    - 인용 관계 그래프

phase_3_synthesis:
  name: "종합 단계"
  actions:
    - 연구 동향 종합
    - 연구 격차(gap) 식별
    - 향후 연구 방향 제안
  output:
    - 종합 리포트
    - 인용 목록 (BibTeX/APA)
```

## MCP Server Integration

```yaml
research_servers:
  semantic_scholar:
    purpose: "학술 논문 검색, DOI 조회, 인용 정보"
    tools:
      - search_paper
      - get_paper
      - get_authors
      - get_citation

  paper_search:
    purpose: "다중 소스 검색 (arXiv, PubMed, bioRxiv)"
    tools:
      - search_arxiv
      - search_pubmed
      - search_biorxiv
      - download_arxiv

  deep_research:
    purpose: "웹 + 학술 통합 연구"
    tools:
      - deep_research
```

## Source Credibility Matrix

```yaml
tier_1_trusted:
  sources:
    - "Peer-reviewed journals (Nature, Science, ACM, IEEE)"
    - "Top-tier conferences (NeurIPS, ICML, ACL, CVPR)"
  trust_level: 95%
  citation_required: always

tier_2_reliable:
  sources:
    - "arXiv with >50 citations"
    - "Workshop papers from top venues"
    - "Technical reports from major labs"
  trust_level: 80%
  citation_required: always

tier_3_moderate:
  sources:
    - "Recent arXiv preprints"
    - "Official documentation"
    - "Engineering blogs from major companies"
  trust_level: 65%
  citation_required: recommended

tier_4_low:
  sources:
    - "Personal blogs"
    - "Forum discussions"
    - "Unverified sources"
  trust_level: 40%
  citation_required: "with [UNVERIFIED] tag"
```

## Output Formats

### Research Report

```markdown
# Research Report: [Topic]

## Executive Summary
[2-3 paragraph overview of key findings]

## Research Questions
1. [Primary research question]
2. [Secondary questions]

## Methodology
- **Search Strategy**: [Keywords, databases, date range]
- **Inclusion Criteria**: [What was included]
- **Exclusion Criteria**: [What was excluded]

## Key Findings

### Finding 1: [Title]
[Description]
**Evidence**: [Citation]
**Confidence**: High/Medium/Low

### Finding 2: [Title]
...

## Research Landscape
[Overview of the field, major players, trends]

## Research Gaps
1. [Gap 1]
2. [Gap 2]

## Future Directions
[Recommendations for future research]

## References
[BibTeX or APA formatted citations]
```

### Citation Formats

```yaml
bibtex:
  example: |
    @article{author2024title,
      title={Paper Title},
      author={Author, First and Second, Author},
      journal={Journal Name},
      year={2024},
      doi={10.1234/example}
    }

apa:
  example: |
    Author, F., & Second, A. (2024). Paper Title. Journal Name, 1(2), 123-456. https://doi.org/10.1234/example
```

## Continuous Research Mode

```yaml
activation:
  keyword: "continuous research" 또는 "--continuous"
  hook: continuous-research.py

workflow:
  1: "research-status.json 생성/로드"
  2: "검색 → 분석 → 종합 사이클 반복"
  3: "RESEARCH_COMPLETE 신호까지 계속"

status_tracking:
  file: ".claude/research-status.json"
  fields:
    - iteration
    - papersFound
    - papersAnalyzed
    - citations
    - phase

completion_signals:
  - "RESEARCH_COMPLETE"
  - "[RESEARCH_DONE]"
  - "[LITERATURE_COMPLETE]"
```

## Quality Checklist

```yaml
before_synthesis:
  - [ ] 최소 5개 이상 핵심 논문 분석?
  - [ ] 다중 소스에서 교차 검증?
  - [ ] 최신 연구 (최근 2-3년) 포함?
  - [ ] 모든 주장에 인용 포함?
  - [ ] 상반된 관점 검토?

after_synthesis:
  - [ ] 연구 격차 식별?
  - [ ] 실용적 시사점 도출?
  - [ ] 인용 형식 일관성?
  - [ ] 불확실한 내용 [UNVERIFIED] 표시?
```

## Integration with Agents

```yaml
delegation:
  librarian:
    when: "증거 기반 검증 필요"
    purpose: "출처 확인, Zero Hallucination"

  oracle:
    when: "복잡한 분석 필요"
    purpose: "심층 분석, 아키텍처 결정"

  researcher:
    when: "서브 주제 탐색"
    purpose: "세부 연구 수행"
```

## Example Usage

```bash
# 학술 논문 중심 연구
/research "transformer attention mechanisms" --academic --max-iterations 15

# 웹 리소스 포함
/research "Claude Code best practices" --web --academic

# BibTeX 인용 포함
/research "RAG systems" --cite bibtex

# 무중단 연속 연구
/research "context engineering" --continuous --max-iterations 20
```
