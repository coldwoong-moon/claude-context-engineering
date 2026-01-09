---
name: moon-research
description: 심층 연구 모드 (학술 논문 + 웹 리서치 + Multi-AI 통합)
allowed-tools: Bash, Read, Write, Glob, Grep, WebSearch, WebFetch, TodoWrite, Task
model: sonnet
argument-hint: <topic> [--academic] [--web] [--cite apa|bibtex|mla]
---

# /moon-research - Unified Deep Research System

> 학술 논문 + 웹 리서치 + Multi-AI 오케스트레이션 통합 연구 시스템

## Quick Start

```bash
# 기본 연구 (학술 + 웹)
/moon-research "transformer attention mechanisms"

# 학술 논문 중심
/moon-research "RAG retrieval augmented generation" --academic --cite bibtex

# 웹 리서치 중심
/moon-research "Claude Code best practices 2025" --web

# 최신 동향 파악
/moon-research "MCP Model Context Protocol" --recent 1
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TOPIC` | 연구 주제 (필수) | - |
| `--academic` | 학술 논문 중심 검색 | false |
| `--web` | 웹 리소스 포함 | true |
| `--cite FORMAT` | 인용 형식 (apa/bibtex/mla/chicago) | apa |
| `--recent N` | 최근 N년 제한 | 5 |
| `--limit N` | 결과 수 제한 | 10 |
| `--depth` | 연구 깊이 (quick/standard/deep) | standard |

## Research Protocol

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MOON RESEARCH PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Phase 1: Query Analysis                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ • Extract core research questions                                │    │
│  │ • Identify keywords and synonyms                                 │    │
│  │ • Determine scope (academic/technical/both)                      │    │
│  │ • Map related domains                                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  ↓                                       │
│  Phase 2: Source Collection                                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Academic:                    Technical:                          │    │
│  │ • Semantic Scholar API       • Official docs                     │    │
│  │ • arXiv (CS, Physics, Math)  • GitHub repos                      │    │
│  │ • PubMed (biomedical)        • Technical blogs                   │    │
│  │                                                                  │    │
│  │ Web:                         Multi-AI:                           │    │
│  │ • WebSearch                  • Gemini (50+ sources)              │    │
│  │ • WebFetch                   • Claude (synthesis)                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  ↓                                       │
│  Phase 3: Analysis & Synthesis                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ • Cross-reference findings                                       │    │
│  │ • Identify patterns and contradictions                          │    │
│  │ • Rate source credibility                                        │    │
│  │ • Generate comparative analysis                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  ↓                                       │
│  Phase 4: Report Generation                                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ • Executive summary                                              │    │
│  │ • Key findings with citations                                    │    │
│  │ • Practical recommendations                                      │    │
│  │ • Knowledge base update                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Multi-AI Integration

대규모 연구 시 자동 위임:

| 상황 | 위임 대상 | 명령 |
|------|-----------|------|
| 50+ 소스 분석 | Gemini CLI | `gemini -p "Research synthesis: $TOPIC" -f sources.md` |
| 문헌 패턴 탐지 | Gemini CLI | `gemini -p "Cross-reference patterns" -f papers/*.md` |
| 복잡한 종합 | Claude | 기본 처리 |

## Source Credibility Matrix

| Tier | Sources | Trust Score |
|------|---------|-------------|
| ⭐⭐⭐⭐⭐ | Peer-reviewed journals, Top-tier conferences | 0.95 |
| ⭐⭐⭐⭐ | arXiv with citations (>50), Workshop papers | 0.80 |
| ⭐⭐⭐ | Recent arXiv, Company tech blogs | 0.65 |
| ⭐⭐ | Personal blogs, Forum posts | 0.40 |
| ⭐ | Unattributed content | 0.10 |

## Output Format

```markdown
# 연구 보고서: [Topic]

**연구일**: YYYY-MM-DD
**범위**: [academic/web/both]
**깊이**: [quick/standard/deep]

---

## 핵심 요약
[3-5 문장의 핵심 발견사항]

## 1. 배경 및 컨텍스트
[연구 주제의 배경 설명]

## 2. 주요 발견

### 2.1 [Finding Category]
- **출처**: [Author et al., Year] ⭐⭐⭐⭐⭐
- **핵심 내용**: [Key insight]
- **방법론**: [Methodology if relevant]
- **한계점**: [Limitations]

### 2.2 [Finding Category]
...

## 3. 비교 분석

| 측면 | 접근법 A | 접근법 B | 접근법 C |
|------|----------|----------|----------|
| 장점 | ... | ... | ... |
| 단점 | ... | ... | ... |
| 적용 사례 | ... | ... | ... |

## 4. 격차 및 기회
- [연구 격차 1]
- [미래 연구 방향]

## 5. 실용적 권장사항
1. [Actionable recommendation]
2. [Actionable recommendation]

## 6. 참고문헌
[선택된 형식으로 정리된 인용]

---
*Generated by /moon-research - Context Engineering Framework*
```

## Knowledge Persistence

연구 결과 자동 저장:
```
.claude/
├── knowledge/
│   └── research/
│       ├── [topic]-[date].md      # 연구 리포트
│       ├── citations.bib          # BibTeX 라이브러리
│       └── search-log.md          # 검색 쿼리 로그
```

## MCP Server Integration

최적의 연구를 위한 MCP 서버:

```yaml
recommended:
  semantic-scholar-mcp:
    purpose: "학술 논문 검색 및 인용"
    tools: [search_paper, get_paper, get_citation]

  paper-search-mcp:
    purpose: "다중 학술 소스 통합 검색"
    sources: [arXiv, PubMed, bioRxiv, Google Scholar]

  deep-research-mcp:
    purpose: "통합 웹 + 학술 연구"
    features: [gap_analysis, synthesis, visualization]
```

## Examples

### 학술 연구
```bash
/moon-research "attention mechanisms in vision transformers" \
  --academic --cite bibtex --recent 3 --depth deep
```

### 기술 동향 파악
```bash
/moon-research "Claude Code MCP integrations" \
  --web --recent 1
```

### 종합 연구
```bash
/moon-research "LLM agent architectures" \
  --academic --web --depth deep --limit 20
```

## Related Commands

- `/moon-loop` - 연속 실행 루프
- `/moon-review` - 코드/아키텍처 리뷰

---

## Execution Start

**Topic**: $ARGUMENTS

### Research Protocol

1. **주제 분석**: 핵심 질문 및 키워드 추출
2. **소스 수집**: 학술 + 웹 소스 수집
3. **분석 및 종합**: 교차 검증 및 패턴 식별
4. **보고서 생성**: 구조화된 연구 보고서 작성
5. **지식 저장**: `.claude/knowledge/research/`에 저장

```
연구를 시작합니다. 완료되면 구조화된 보고서를 제공하겠습니다.
```
