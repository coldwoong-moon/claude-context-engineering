# Critical Review Skill - 다중 관점 비판 리뷰

> 코드, 아키텍처, 문서를 다중 관점에서 체계적으로 리뷰하는 스킬
> 무중단 리뷰 모드 지원 (continuous-review.py 훅 연동)

## Activation

```bash
# 매직 키워드로 활성화
review <target>
리뷰 <대상>
/review <target>

# 명령어로 활성화
/critical-review src/ --continuous --all-perspectives
```

## 3-Phase Review Framework

```yaml
phase_1_critical_review:
  name: "비판적 분석 단계"
  purpose: "객관적 현상태 분석"
  perspectives:
    - security: "보안 취약점, OWASP Top 10"
    - performance: "시간/공간 복잡도, 병목점"
    - architecture: "SOLID, DRY, KISS 준수"
    - maintainability: "가독성, 테스트 용이성"
    - correctness: "로직 오류, 엣지 케이스"
    - best_practices: "컨벤션, 패턴, 안티패턴"

phase_2_feedback:
  name: "피드백 단계"
  purpose: "구체적 개선점 제시"
  requirements:
    - 비판은 구체적 증거와 함께
    - 문제점마다 해결 방향 제시
    - 우선순위 명시 (Critical/High/Medium/Low)
    - 코드 예시로 개선안 시연

phase_3_feedforward:
  name: "피드포워드 단계"
  purpose: "미래 지향적 제안"
  focus:
    - 확장성 고려사항
    - 기술 부채 예방
    - 아키텍처 진화 경로
    - 팀 역량 성장 기회
```

## Review Perspectives

### 🛡️ Security Perspective

```yaml
checklist:
  injection:
    - "SQL Injection 취약점?"
    - "XSS (Cross-Site Scripting)?"
    - "Command Injection?"
  authentication:
    - "인증 우회 가능성?"
    - "세션 관리 문제?"
    - "비밀번호 저장 방식?"
  authorization:
    - "권한 상승 가능성?"
    - "IDOR (Insecure Direct Object Reference)?"
  data:
    - "민감 데이터 암호화?"
    - "로그에 민감 정보?"

tools:
  - "OWASP ZAP"
  - "npm audit / pip-audit"
  - "Snyk"
```

### ⚡ Performance Perspective

```yaml
checklist:
  time_complexity:
    - "O(n²) 이상 복잡도?"
    - "불필요한 반복?"
  space_complexity:
    - "메모리 누수?"
    - "큰 객체 복사?"
  database:
    - "N+1 쿼리?"
    - "인덱스 부재?"
  network:
    - "불필요한 API 호출?"
    - "페이로드 크기?"
  caching:
    - "캐싱 기회?"
    - "캐시 무효화?"

tools:
  - "Profiler"
  - "Lighthouse"
  - "Query Analyzer"
```

### 🏗️ Architecture Perspective

```yaml
checklist:
  solid:
    - "단일 책임 원칙 (SRP)?"
    - "개방-폐쇄 원칙 (OCP)?"
    - "리스코프 치환 원칙 (LSP)?"
    - "인터페이스 분리 원칙 (ISP)?"
    - "의존성 역전 원칙 (DIP)?"
  dependencies:
    - "순환 의존성?"
    - "불필요한 의존성?"
  scalability:
    - "수평 확장 가능?"
    - "상태 관리?"
  patterns:
    - "적절한 디자인 패턴?"
    - "안티패턴 존재?"
```

### 🔧 Maintainability Perspective

```yaml
checklist:
  readability:
    - "명확한 네이밍?"
    - "적절한 주석?"
    - "일관된 스타일?"
  testability:
    - "단위 테스트 가능?"
    - "의존성 주입?"
    - "모킹 용이?"
  documentation:
    - "API 문서화?"
    - "README 최신?"
    - "변경 이력?"
```

## Severity Classification

```yaml
critical:
  icon: "🔴"
  description: "즉각적 익스플로잇 가능, 데이터 손실 위험"
  response_time: "24시간 내"
  examples:
    - "SQL Injection"
    - "인증 우회"
    - "원격 코드 실행"

high:
  icon: "🟠"
  description: "악용 가능한 취약점, 심각한 성능 문제"
  response_time: "1주 내"
  examples:
    - "XSS"
    - "N+1 쿼리"
    - "메모리 누수"

medium:
  icon: "🟡"
  description: "조건부 취약점, 유지보수 문제"
  response_time: "1개월 내"
  examples:
    - "CSRF"
    - "코드 중복"
    - "불충분한 테스트"

low:
  icon: "🟢"
  description: "최소 위험, 개선 권장"
  response_time: "다음 릴리스"
  examples:
    - "네이밍 컨벤션"
    - "주석 부족"
    - "코드 스타일"
```

## Output Format

```markdown
# Critical Review: [Target]

## Executive Summary

**Overall Score**: [A-F] / [0-100]
**Risk Level**: Critical/High/Medium/Low
**Review Date**: YYYY-MM-DD

### Key Findings
- 🔴 Critical: [count]개
- 🟠 High: [count]개
- 🟡 Medium: [count]개
- 🟢 Low: [count]개

---

## Phase 1: Critical Review

### 🛡️ Security Analysis
[Findings with evidence]

**Issues Found:**
| Severity | Issue | Location | Evidence |
|----------|-------|----------|----------|
| 🔴 Critical | ... | file:line | ... |

### ⚡ Performance Analysis
[Findings with evidence]

### 🏗️ Architecture Analysis
[Findings with evidence]

---

## Phase 2: Feedback

### Critical Issues (Immediate Action Required)

#### Issue 1: [Title]
- **Location**: `file:line`
- **Problem**: [Description]
- **Impact**: [What could go wrong]
- **Solution**: [How to fix]
- **Code Example**:
```language
// Before
...
// After
...
```

### High Priority Issues
...

---

## Phase 3: Feedforward

### Long-term Recommendations
1. [Recommendation with rationale]
2. [Recommendation with rationale]

### Technical Debt Prevention
- [Strategy]

### Growth Opportunities
- [Learning suggestion]

---

## Action Items

| Priority | Action | Owner | Deadline |
|----------|--------|-------|----------|
| 🔴 | ... | ... | ... |
| 🟠 | ... | ... | ... |
```

## Continuous Review Mode

```yaml
activation:
  keyword: "continuous review" 또는 "--continuous"
  hook: continuous-review.py

workflow:
  1: "review-status.json 생성/로드"
  2: "관점 순환 리뷰 (security → performance → ...)"
  3: "REVIEW_COMPLETE 신호까지 계속"

perspective_rotation:
  order:
    - security
    - performance
    - architecture
    - maintainability
    - correctness
    - best_practices

status_tracking:
  file: ".claude/review-status.json"
  fields:
    - iteration
    - currentPerspective
    - completedPerspectives
    - issues

completion_signals:
  - "REVIEW_COMPLETE"
  - "[REVIEW_DONE]"
  - "[CRITICAL_REVIEW_COMPLETE]"
```

## Integration with Agents

```yaml
delegation:
  oracle:
    when: "복잡한 아키텍처 결정"
    purpose: "심층 분석"

  librarian:
    when: "베스트 프랙티스 확인"
    purpose: "증거 기반 권고"

  test_writer:
    when: "테스트 커버리지 문제"
    purpose: "테스트 코드 생성"

  task_worker:
    when: "자동 수정 가능한 이슈"
    purpose: "코드 수정"
```

## Example Usage

```bash
# 전체 관점 리뷰
/critical-review src/ --all-perspectives

# 보안 중심 리뷰
/critical-review src/auth/ --focus security

# 아키텍처 리뷰
/critical-review --scope architecture

# 무중단 연속 리뷰
/critical-review src/ --continuous --max-iterations 12

# PR 리뷰
/critical-review --pr 123
```
