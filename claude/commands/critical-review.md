# /critical-review - 다중 관점 비판 리뷰 명령어

> 코드, 아키텍처, 문서를 다중 관점에서 체계적으로 리뷰
> 무중단 연속 리뷰 모드 지원

## Quick Start

```bash
# 기본 사용
/critical-review src/

# 보안 중심 리뷰
/critical-review src/auth/ --focus security

# 무중단 연속 리뷰
/critical-review src/ --continuous --max-iterations 12

# PR 리뷰
/critical-review --pr 123
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TARGET` | 리뷰 대상 (디렉토리, 파일, PR) | . |
| `--focus PERSPECTIVE` | 특정 관점 집중 | all |
| `--continuous` | 무중단 연속 리뷰 모드 | false |
| `--max-iterations N` | 최대 반복 횟수 | 12 |
| `--all-perspectives` | 모든 관점 순환 | true |
| `--pr NUMBER` | PR 리뷰 모드 | - |
| `--depth LEVEL` | 리뷰 깊이 (quick, standard, deep) | standard |
| `--output FORMAT` | 출력 형식 (markdown, json) | markdown |

## 3-Phase Review Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                    3-PHASE REVIEW FRAMEWORK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1: CRITICAL REVIEW                                       │
│   ┌────────────────────────────────────────┐                     │
│   │ 목적: 객관적 현상태 분석                │                     │
│   │                                         │                     │
│   │ 관점 순환:                              │                     │
│   │ 🛡️ Security → ⚡ Performance →          │                     │
│   │ 🏗️ Architecture → 🔧 Maintainability → │                     │
│   │ ✅ Correctness → 📚 Best Practices      │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Phase 2: FEEDBACK                                              │
│   ┌────────────────────────────────────────┐                     │
│   │ 목적: 구체적 개선점 제시                │                     │
│   │                                         │                     │
│   │ • 비판 + 구체적 증거                    │                     │
│   │ • 문제점 + 해결 방향                    │                     │
│   │ • 우선순위 분류                         │                     │
│   │ • 코드 예시 시연                        │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Phase 3: FEEDFORWARD                                           │
│   ┌────────────────────────────────────────┐                     │
│   │ 목적: 미래 지향적 제안                  │                     │
│   │                                         │                     │
│   │ • 확장성 고려사항                       │                     │
│   │ • 기술 부채 예방                        │                     │
│   │ • 아키텍처 진화 경로                    │                     │
│   │ • 학습 기회                             │                     │
│   └────────────────────────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Review Perspectives

### 🛡️ Security
```yaml
focus:
  - SQL/XSS/Command Injection
  - Authentication & Authorization
  - Data Protection
  - OWASP Top 10

checklist:
  - "[ ] SQL Injection 취약점?"
  - "[ ] XSS 취약점?"
  - "[ ] 인증/인가 문제?"
  - "[ ] 민감 데이터 노출?"
```

### ⚡ Performance
```yaml
focus:
  - Time & Space Complexity
  - Database Queries
  - Memory Management
  - Caching Opportunities

checklist:
  - "[ ] O(n²) 이상 복잡도?"
  - "[ ] N+1 쿼리?"
  - "[ ] 메모리 누수?"
  - "[ ] 캐싱 기회?"
```

### 🏗️ Architecture
```yaml
focus:
  - SOLID Principles
  - Dependencies
  - Scalability
  - Design Patterns

checklist:
  - "[ ] 단일 책임 원칙?"
  - "[ ] 순환 의존성?"
  - "[ ] 확장성?"
  - "[ ] 적절한 패턴?"
```

### 🔧 Maintainability
```yaml
focus:
  - Readability
  - Testability
  - Documentation

checklist:
  - "[ ] 명확한 네이밍?"
  - "[ ] 테스트 커버리지?"
  - "[ ] 충분한 문서?"
```

### ✅ Correctness
```yaml
focus:
  - Logic Errors
  - Edge Cases
  - Error Handling

checklist:
  - "[ ] 로직 오류?"
  - "[ ] 엣지 케이스?"
  - "[ ] Null 처리?"
```

### 📚 Best Practices
```yaml
focus:
  - Conventions
  - Patterns
  - Anti-patterns

checklist:
  - "[ ] 코딩 컨벤션?"
  - "[ ] 안티패턴?"
  - "[ ] 에러 로깅?"
```

## Severity Classification

| Level | Icon | Description | Response |
|-------|------|-------------|----------|
| Critical | 🔴 | 즉각적 익스플로잇 가능 | 24시간 내 |
| High | 🟠 | 악용 가능한 취약점 | 1주 내 |
| Medium | 🟡 | 조건부 취약점 | 1개월 내 |
| Low | 🟢 | 최소 위험 | 다음 릴리스 |

## Continuous Mode

무중단 연속 리뷰 모드는 `continuous-review.py` 훅과 연동:

```yaml
activation: "--continuous"

status_file: ".claude/review-status.json"
log_file: ".claude/review-log.md"
issues_file: ".claude/review-issues.md"

completion_signals:
  - "REVIEW_COMPLETE"
  - "[REVIEW_DONE]"

workflow:
  1: "Stop Hook이 완료 신호 확인"
  2: "신호 없으면 다음 관점으로 순환"
  3: "모든 관점 완료 또는 완료 신호까지 반복"
```

## Output Format

```markdown
# Critical Review: [Target]

## Executive Summary
**Overall Score**: B / 78
**Risk Level**: Medium
**Issues**: 🔴 1 | 🟠 3 | 🟡 5 | 🟢 8

---

## Phase 1: Critical Review

### 🛡️ Security Analysis
[발견 사항]

| Severity | Issue | Location |
|----------|-------|----------|
| 🔴 | SQL Injection | auth.ts:42 |

---

## Phase 2: Feedback

### Critical Issues

#### SQL Injection in auth.ts:42
- **Problem**: 직접 문자열 연결 사용
- **Impact**: 데이터베이스 전체 노출 가능
- **Solution**: Parameterized query 사용

---

## Phase 3: Feedforward

### Long-term Recommendations
1. ORM 도입 검토
2. 보안 린터 추가

---

## Action Items
| Priority | Action | Deadline |
|----------|--------|----------|
| 🔴 | SQL Injection 수정 | 24h |
```

## Examples

### 1. 전체 관점 리뷰
```bash
/critical-review src/ --all-perspectives --depth deep
```

### 2. 보안 집중 리뷰
```bash
/critical-review src/api/ --focus security
```

### 3. 무중단 연속 리뷰
```bash
/critical-review src/ --continuous --max-iterations 12
```

### 4. PR 리뷰
```bash
/critical-review --pr 456 --depth standard
```

### 5. 아키텍처 리뷰
```bash
/critical-review --focus architecture --depth deep
```

## Delegation

리뷰 작업은 다음 에이전트에 위임될 수 있습니다:

| Agent | When | Purpose |
|-------|------|---------|
| `oracle` | 복잡한 아키텍처 | 심층 분석 |
| `librarian` | 베스트 프랙티스 | 증거 기반 권고 |
| `test_writer` | 테스트 부족 | 테스트 생성 |
| `task_worker` | 자동 수정 | 코드 수정 |

## Related

- `/review` - 기본 리뷰
- `/verify-app` - 앱 검증
- `review` 매직 키워드
- `continuous-review.py` 훅
