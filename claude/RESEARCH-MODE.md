# RESEARCH-MODE.md - 심층 연구 모드

Claude Code Context Engineering의 심층 연구 모드 가이드.

## Overview

Research Mode는 학술 논문, 기술 문서, 웹 리소스를 체계적으로 탐색하고 분석하여
**증거 기반의 심층 연구**를 수행하는 특화 모드입니다.

## Quick Start

```bash
# 1. MCP 서버 설치
python scripts/setup.py install

# 2. 연구 모드 MCP 추가 설치
./scripts/install-research-mcp.sh

# 3. Claude Code에서 사용
/research "your research topic" --academic
```

## Core Philosophy

```yaml
principles:
  evidence_based: "모든 주장은 신뢰할 수 있는 출처로 뒷받침"
  systematic: "체계적 문헌 검토 방법론 적용"
  reproducible: "연구 과정 및 검색 쿼리 문서화"
  comprehensive: "다중 소스 교차 검증"
  current: "최신 연구 동향 우선"
```

## MCP Server Stack

### Tier 1: 핵심 서버 (필수)

#### Semantic Scholar MCP
```yaml
server: semantic-scholar-mcp
source: github.com/FujishigeTemma/semantic-scholar-mcp
purpose: 학술 논문 검색 및 메타데이터

tools:
  search_paper:
    description: "키워드 기반 논문 검색"
    filters: [year, fields_of_study, open_access, venue]

  get_paper:
    description: "논문 상세 정보 조회"
    identifiers: [DOI, ArXiv, S2, PMID, MAG, ACL]

  get_authors:
    description: "저자 정보 및 출판 이력"

  get_citation:
    description: "인용 내보내기"
    formats: [BibTeX, APA, MLA, Chicago]

rate_limits:
  without_key: "100 requests / 5 minutes"
  with_key: "1 request / second (higher on request)"
```

#### Paper Search MCP
```yaml
server: paper-search-mcp
source: github.com/openags/paper-search-mcp
purpose: 다중 학술 소스 통합 검색

sources:
  implemented:
    - arXiv (CS, Physics, Math, etc.)
    - PubMed (Biomedical)
    - bioRxiv (Biology preprints)
    - medRxiv (Medical preprints)
    - Google Scholar
    - IACR ePrint (Cryptography)
    - Semantic Scholar

  planned:
    - IEEE Xplore
    - ACM Digital Library
    - Springer Link
    - Web of Science

tools:
  search_<source>: "소스별 검색"
  download_<source>: "PDF 다운로드"
```

### Tier 2: 확장 서버 (권장)

#### Deep Research MCP
```yaml
server: deep-research-mcp
source: github.com/mcherukara/Claude-Deep-Research
purpose: 통합 웹 + 학술 연구

methodology:
  1_exploration: "초기 정보 수집"
  2_synthesis: "예비 종합 및 시각화 제안"
  3_gap_analysis: "격차 식별 및 추가 연구"
  4_integration: "종합 통합"
  5_citation: "APA 형식 인용"

config:
  MAX_CONTENT_SIZE: 8000
  MAX_RESULTS: 3
  sources: ["web", "academic", "both"]
```

#### Perplexity/OpenAI Deep Research
```yaml
server: deep-research-mcp (pminervini)
source: github.com/pminervini/deep-research-mcp
purpose: AI 기반 심층 연구

providers:
  openai:
    model: "o4-mini-deep-research-2025-06-26"
    features: [web_search, code_interpreter]

  perplexity:
    endpoint: "sonar-deep-research"

  open_deep_research:
    model: "litellm-compatible"
```

### Tier 3: 보조 도구

```yaml
fetch_mcp:
  purpose: "웹 페이지 콘텐츠 가져오기"

puppeteer_mcp:
  purpose: "JavaScript 렌더링 페이지 접근"

filesystem_mcp:
  purpose: "연구 결과 로컬 저장"
```

## Installation

### 자동 설치 (권장)

```bash
# 연구 MCP 서버 설치 스크립트
cd claude-context-engineering
./scripts/install-research-mcp.sh
```

### 수동 설치

#### 1. Semantic Scholar MCP

```bash
# API 키 발급: https://www.semanticscholar.org/product/api
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# Claude Code에 추가
claude mcp add semantic-scholar \
  -e SEMANTIC_SCHOLAR_API_KEY="$SEMANTIC_SCHOLAR_API_KEY" \
  -- uvx --from git+https://github.com/FujishigeTemma/semantic-scholar-mcp \
  semantic-scholar-mcp serve
```

#### 2. Paper Search MCP

```bash
# Smithery 통한 설치
npx -y @smithery/cli install @openags/paper-search-mcp --client claude

# 또는 수동 설치
claude mcp add paper-search \
  -- uvx --from git+https://github.com/openags/paper-search-mcp \
  python -m paper_search_mcp.server
```

#### 3. Deep Research MCP

```bash
# 저장소 클론
git clone https://github.com/mcherukara/Claude-Deep-Research ~/.claude/mcp/deep-research

# 의존성 설치
pip install mcp httpx beautifulsoup4

# Claude Desktop 설정에 추가
# ~/Library/Application Support/Claude/claude_desktop_config.json
```

## Research Workflows

### 1. 학술 논문 중심 연구

```yaml
workflow: academic_research
trigger: "/research <topic> --academic"

steps:
  1_keyword_extraction:
    action: "연구 주제에서 핵심 키워드 추출"
    output: ["primary_terms", "related_terms", "synonyms"]

  2_initial_search:
    action: "Semantic Scholar로 초기 검색"
    params:
      year_range: "2020-2025"
      fields: "auto-detected"
      limit: 20
    output: "candidate_papers"

  3_relevance_filtering:
    action: "제목, 초록 기반 관련성 필터링"
    criteria:
      - title_match_score > 0.7
      - abstract_relevance > 0.6
      - citation_count > 10
    output: "filtered_papers"

  4_deep_analysis:
    action: "상위 논문 심층 분석"
    for_each_paper:
      - extract_methodology
      - identify_key_findings
      - note_limitations
      - track_citations

  5_citation_network:
    action: "인용 네트워크 탐색"
    methods:
      - cited_by: "이 논문을 인용한 최신 논문"
      - references: "이 논문이 인용한 핵심 논문"

  6_synthesis:
    action: "연구 동향 종합"
    output:
      - research_landscape_map
      - key_findings_summary
      - identified_gaps
      - future_directions

  7_report_generation:
    action: "구조화된 리포트 생성"
    format: "academic_report_template"
    citations: "requested_format"
```

### 2. 기술 탐색 연구

```yaml
workflow: technology_exploration
trigger: "/research <tech-topic>"

steps:
  1_landscape_scan:
    sources: ["web", "academic", "github"]
    focus: ["official_docs", "tutorials", "benchmarks"]

  2_implementation_analysis:
    action: "주요 구현체 분석"
    aspects:
      - architecture_patterns
      - performance_characteristics
      - adoption_metrics

  3_comparison:
    action: "대안 기술과 비교"
    dimensions:
      - features
      - performance
      - ecosystem
      - learning_curve

  4_practical_recommendations:
    action: "실용적 권장사항 도출"
```

### 3. 문헌 리뷰

```yaml
workflow: literature_review
trigger: "/literature-review <topic>"

methodology: "PRISMA-inspired"

steps:
  identification:
    databases: ["Semantic Scholar", "arXiv", "PubMed", "Google Scholar"]
    query_construction: "Boolean operators + field-specific terms"

  screening:
    level_1: "Title/Abstract screening"
    level_2: "Full-text assessment"

  eligibility:
    inclusion_criteria: "user-defined or auto-suggested"
    exclusion_criteria: "user-defined or auto-suggested"

  synthesis:
    approach: ["narrative", "thematic", "meta-analytic"]

  reporting:
    format: "systematic_review_template"
    includes: ["PRISMA_flowchart", "evidence_table", "quality_assessment"]
```

## Research Quality Framework

### Source Credibility Matrix

```yaml
tier_1_highest:
  sources:
    - peer_reviewed_journals
    - top_tier_conferences (NeurIPS, ICML, ACL, CVPR, etc.)
  trust_score: 0.95
  verification: "DOI + venue verification"

tier_2_high:
  sources:
    - arXiv_with_citations (>50)
    - workshop_papers
    - technical_reports (major labs)
  trust_score: 0.80
  verification: "Author credentials + citation analysis"

tier_3_medium:
  sources:
    - arXiv_recent
    - company_blogs (established)
    - official_documentation
  trust_score: 0.65
  verification: "Cross-reference with tier 1-2"

tier_4_lower:
  sources:
    - personal_blogs
    - social_media
    - forum_posts
  trust_score: 0.40
  verification: "Use as leads only, verify independently"

tier_5_avoid:
  sources:
    - unattributed_content
    - known_unreliable_sources
  trust_score: 0.10
  action: "Exclude unless exceptional circumstances"
```

### Citation Verification Checklist

```yaml
verification_steps:
  1_doi_check:
    action: "Verify DOI resolves correctly"
    tool: "doi.org lookup"

  2_author_verification:
    action: "Confirm author exists and is affiliated"
    tool: "Semantic Scholar author lookup"

  3_publication_date:
    action: "Confirm publication date"
    importance: "Critical for recent claims"

  4_retraction_check:
    action: "Check for retractions or corrections"
    tool: "Retraction Watch database"

  5_citation_context:
    action: "Verify citation supports the claim made"
    common_issues:
      - over_generalization
      - context_stripping
      - contradictory_findings_ignored
```

## Output Templates

### Academic Research Report

```markdown
# Research Report: [Topic]

**Date**: [YYYY-MM-DD]
**Query**: [Original research query]
**Methodology**: [Workflow used]

---

## Executive Summary

[3-5 sentences capturing key findings]

## 1. Introduction & Background

### 1.1 Research Question
[Clear articulation of the research question]

### 1.2 Scope & Limitations
[What is and isn't covered]

## 2. Methodology

### 2.1 Search Strategy
- **Databases**: [List of sources searched]
- **Query Terms**: [Search terms used]
- **Filters**: [Year range, field, etc.]
- **Date of Search**: [When searches were conducted]

### 2.2 Selection Criteria
- **Inclusion**: [Criteria]
- **Exclusion**: [Criteria]

## 3. Findings

### 3.1 [Theme/Category 1]

**Key Papers**:
1. [Author et al. (Year)] - [Key contribution]
2. [Author et al. (Year)] - [Key contribution]

**Synthesis**: [What the evidence shows]

### 3.2 [Theme/Category 2]
[...]

## 4. Research Landscape

[Visual or tabular representation of the field]

| Approach | Key Works | Strengths | Limitations |
|----------|-----------|-----------|-------------|
| ...      | ...       | ...       | ...         |

## 5. Gaps & Opportunities

1. [Gap 1]: [Description and potential research direction]
2. [Gap 2]: [Description and potential research direction]

## 6. Conclusions & Recommendations

[Summary of findings and actionable recommendations]

## References

[Citations in requested format]
```

## Mode Switching

### 활성화

```bash
# 명시적 활성화
/research <topic>

# 매직 키워드 (hooks 통해)
research: <topic>
연구: <topic>
리서치: <topic>
```

### 연구 모드 상태 확인

```bash
/research-status
```

### 모드 전환

```yaml
mode_transitions:
  from_default_to_research:
    trigger: "/research"
    activates:
      - research_mcp_servers
      - citation_tracking
      - source_verification

  from_research_to_default:
    trigger: "/exit-research" or session_end
    saves:
      - research_notes
      - citation_library
      - search_history
```

## Integration with Context Engineering

### Knowledge Persistence

연구 결과는 자동으로 `.claude/knowledge/` 디렉토리에 저장됩니다:

```
.claude/
├── knowledge/
│   ├── research/
│   │   ├── [topic]-[date].md      # 연구 리포트
│   │   ├── citations.bib          # BibTeX 인용 라이브러리
│   │   └── search-log.md          # 검색 쿼리 로그
│   └── ...
```

### Hook Integration

```yaml
hooks:
  UserPromptSubmit:
    - magic-keywords.py  # "research", "연구" 등 감지

  PostToolUse:
    - research-logger.py  # 연구 활동 로깅

  PreCompact:
    - research-state-saver.py  # 연구 상태 보존
```

## Best Practices

### 1. 명확한 연구 질문 정의
- 구체적이고 측정 가능한 질문
- 범위 제한 (너무 광범위하면 품질 저하)

### 2. 다중 소스 교차 검증
- 단일 소스에 의존하지 않음
- 상충되는 증거 명시적 처리

### 3. 최신성과 관련성 균형
- 최신 연구 우선하되
- 기초가 되는 고전적 연구도 포함

### 4. 체계적 문서화
- 모든 검색 쿼리 기록
- 제외 결정 이유 문서화
- 재현 가능한 방법론

### 5. 비판적 평가
- 연구의 한계점 인식
- 잠재적 편향 고려
- 일반화 가능성 평가

## Troubleshooting

### MCP 서버 연결 실패

```bash
# 서버 상태 확인
claude mcp list

# 로그 확인
claude mcp logs semantic-scholar

# 재설치
claude mcp remove semantic-scholar
claude mcp add semantic-scholar ...
```

### API 한도 초과

```yaml
solutions:
  semantic_scholar:
    - "API 키 발급으로 한도 증가"
    - "요청 간 딜레이 추가"

  general:
    - "캐시 활용"
    - "배치 요청으로 통합"
```

### 검색 결과 부족

```yaml
troubleshooting:
  - "검색어 변형 (동의어, 관련어)"
  - "영어 + 원어 병행 검색"
  - "시간 범위 확대"
  - "다른 데이터베이스 시도"
```

## Resources

### API Key 발급
- Semantic Scholar: https://www.semanticscholar.org/product/api
- arXiv API: 키 불필요 (rate limit 주의)
- PubMed: https://www.ncbi.nlm.nih.gov/account/

### 참고 문서
- [MCP Specification](https://modelcontextprotocol.io/)
- [Semantic Scholar API Docs](https://api.semanticscholar.org/)
- [arXiv API Docs](https://arxiv.org/help/api/)
