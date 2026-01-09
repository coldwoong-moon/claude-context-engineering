---
name: moon-review
description: 비판적 코드/아키텍처 리뷰 (Multi-Perspective + Feedback + Feedforward)
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite, Task
model: sonnet
argument-hint: <target> [--scope code|arch|security|perf|all] [--depth quick|standard|deep]
---

# /moon-review - Unified Critical Review System

> 다중 관점 비판적 분석 + 피드백 + 피드포워드 통합 리뷰 시스템

## Quick Start

```bash
# 기본 코드 리뷰
/moon-review src/components/

# 아키텍처 심층 리뷰
/moon-review . --scope arch --depth deep

# 보안 중심 리뷰
/moon-review src/auth/ --scope security

# 종합 리뷰
/moon-review . --scope all --depth standard
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TARGET` | 리뷰 대상 (파일/디렉토리/PR#) | . |
| `--scope` | 리뷰 범위 | code |
| `--depth` | 분석 깊이 | standard |
| `--output` | 출력 형식 (report/inline/checklist) | report |

### Scope Options

| Scope | Focus |
|-------|-------|
| `code` | 코드 품질, 가독성, 유지보수성 |
| `arch` | 아키텍처, 설계 패턴, 의존성 |
| `security` | 보안 취약점, OWASP Top 10 |
| `perf` | 성능 병목점, 최적화 기회 |
| `docs` | 문서화 품질 및 완전성 |
| `all` | 종합 리뷰 |

### Depth Options

| Depth | Description |
|-------|-------------|
| `quick` | 빠른 스캔 (주요 이슈만, ~5분) |
| `standard` | 표준 리뷰 (균형잡힌 분석, ~15분) |
| `deep` | 심층 분석 (모든 관점, ~30분+) |

## Review Protocol

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MOON REVIEW PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Phase 1: Critical Review (현상태 분석)                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Multi-Perspective Analysis:                                      │    │
│  │ • Code Quality: 복잡도, 가독성, 유지보수성                        │    │
│  │ • Architecture: SOLID, 결합도, 응집도                            │    │
│  │ • Security: 입력 검증, 인증/인가, 데이터 노출                     │    │
│  │ • Performance: 알고리즘 복잡도, 메모리, 캐싱                      │    │
│  │ • Testing: 커버리지, 엣지 케이스                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  ↓                                       │
│  Phase 2: Feedback (구체적 개선점)                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ • 문제점마다 구체적 해결 방향 제시                                │    │
│  │ • 코드 예시로 개선안 시연                                         │    │
│  │ • 우선순위 명시 (Critical/High/Medium/Low)                        │    │
│  │ • 예상 공수 제시                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  ↓                                       │
│  Phase 3: Feedforward (미래 지향적 제안)                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ • 확장성 고려사항                                                 │    │
│  │ • 기술 부채 예방                                                  │    │
│  │ • 아키텍처 진화 경로                                              │    │
│  │ • 팀 역량 성장 기회                                               │    │
│  │ • 자동화 및 도구 활용                                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Multi-AI Integration

대규모 리뷰 시 자동 위임:

| 상황 | 위임 대상 | 명령 |
|------|-----------|------|
| 30+ 파일 분석 | Gemini CLI | `gemini -p "Comprehensive code review" -f "src/**/*"` |
| 크로스파일 패턴 | Gemini CLI | `gemini -p "Cross-file inconsistencies" -f "**/*.ts"` |
| 복잡한 추론 | Claude | 기본 처리 |

## Severity Levels

| Level | 정의 | 대응 시간 |
|-------|------|----------|
| 🔴 Critical | 즉각적 익스플로잇/장애 가능 | 24시간 내 |
| 🟠 High | 악용 가능/주요 버그 | 1주 내 |
| 🟡 Medium | 조건부 문제 | 1개월 내 |
| 🟢 Low | 최소 위험, 개선 권장 | 다음 릴리스 |

## Quality Metrics

| Metric | Excellent | Good | Needs Work | Critical |
|--------|-----------|------|------------|----------|
| Cyclomatic Complexity | <10 | 10-15 | 15-25 | >25 |
| Function Length | <30 lines | 30-50 | 50-100 | >100 |
| Nesting Depth | <3 | 3-4 | 4-6 | >6 |
| Test Coverage | >80% | 60-80% | 40-60% | <40% |
| Documentation | >90% | 70-90% | 50-70% | <50% |

## Output Format

```markdown
# 리뷰 보고서: [Target]

**리뷰 대상**: [파일/디렉토리]
**범위**: [code|arch|security|perf|all]
**깊이**: [quick|standard|deep]
**리뷰일**: YYYY-MM-DD

---

## 요약

### 전체 평가: [A-F] ([점수]/100)

| 영역 | 점수 | 상태 |
|------|------|------|
| Code Quality | 75/100 | ⚠️ Needs Improvement |
| Architecture | 85/100 | ✅ Good |
| Security | 60/100 | 🚨 Critical Issues |
| Performance | 80/100 | ✅ Good |
| Documentation | 45/100 | ❌ Poor |

### 핵심 발견
- 🔴 [Critical Issue]
- 🟠 [High Priority Issue]
- 🟡 [Medium Priority Issue]

---

## 1. Critical Review (현상태 분석)

### 1.1 Code Quality

#### Strengths
- [강점 1]
- [강점 2]

#### Issues Found

| ID | Severity | Location | Issue | Impact |
|----|----------|----------|-------|--------|
| CQ-001 | 🔴 | src/auth.ts:45 | SQL Injection | Data breach |
| CQ-002 | 🟠 | src/api.ts:120 | Unhandled error | Crash |

### 1.2 Architecture
[아키텍처 분석]

### 1.3 Security
[보안 분석]

### 1.4 Performance
[성능 분석]

---

## 2. Feedback (구체적 개선안)

### Issue CQ-001: SQL Injection

**현재 코드**:
```typescript
// ❌ 취약한 코드
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

**개선안**:
```typescript
// ✅ Parameterized query
const query = `SELECT * FROM users WHERE id = ?`;
db.query(query, [userId]);
```

**우선순위**: 🔴 Critical - 즉시 수정 필요
**예상 공수**: 30분
**관련 파일**: src/auth.ts, src/db.ts

---

## 3. Feedforward (미래 방향)

### 3.1 단기 (1-2주)
| 제안 | 근거 | 기대 효과 |
|------|------|----------|
| ESLint 규칙 강화 | 코드 품질 이슈 반복 | 자동 품질 관리 |

### 3.2 중기 (1-3개월)
| 제안 | 근거 | 기대 효과 |
|------|------|----------|
| 모듈 분리 | SRP 위반 | 유지보수성 향상 |

### 3.3 장기 (3-6개월)
| 제안 | 근거 | 기대 효과 |
|------|------|----------|
| 마이크로서비스 전환 | 확장성 한계 | 독립 배포 가능 |

---

## 4. Action Items

### Immediate (24시간 내)
- [ ] CQ-001: SQL Injection 수정
- [ ] CQ-002: Error handling 추가

### This Sprint
- [ ] 테스트 커버리지 60% 달성
- [ ] ESLint 규칙 업데이트

### Next Sprint
- [ ] 모듈 분리 계획 수립

---

## 5. Learning Opportunities
1. **OWASP Top 10** - 보안 베스트 프랙티스
2. **Clean Code** - 클린 코드 원칙

---
*Generated by /moon-review - Context Engineering Framework*
```

## Integration

리뷰 결과 자동 처리:
1. **Critical 이슈** → TodoWrite (즉시 추적)
2. **개선 권장** → 선택적 적용
3. **Feedforward** → 지식 베이스 저장

## Examples

### 코드 리뷰
```bash
/moon-review src/components/ --scope code --depth standard
```

### 보안 감사
```bash
/moon-review . --scope security --depth deep --output checklist
```

### PR 리뷰
```bash
/moon-review PR#123 --scope all
```

### 아키텍처 평가
```bash
/moon-review . --scope arch --depth deep
```

## Related Commands

- `/moon-loop` - 연속 실행 루프
- `/moon-research` - 심층 연구
- `/verify-app` - 앱 검증

---

## Execution Start

**Target**: $ARGUMENTS

### Review Protocol

1. **범위 분석**: 리뷰 대상 스캔 및 분류
2. **Critical Review**: 다중 관점 현상태 분석
3. **Feedback**: 구체적 개선안 도출
4. **Feedforward**: 미래 지향적 제안
5. **Action Items**: 우선순위별 액션 아이템

```
리뷰를 시작합니다. 완료되면 구조화된 리뷰 보고서를 제공하겠습니다.
```
