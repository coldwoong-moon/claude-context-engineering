# Context Engineering Framework

> 최소한의 컨텍스트로 최대의 자동화

## Core Principles

```yaml
evidence_first: "증거 없는 주장 금지. 모든 코드 참조에 파일:라인"
spec_before_code: "구현 전 스펙 세분화. Feature → Story → Atomic Task"
evolution_loop: "모든 작업 결과 → 메트릭 수집 → 템플릿 개선"
native_first: "Claude Code 네이티브 기능 우선 활용"
```

## Workflow Protocol

### 1. Pre-Implementation (MANDATORY)
```
요청 분석 → 요구사항 추출 → 설계 검토 → 작업 원자화 → 승인 → 구현
         ↓         ↓           ↓            ↓
      implicit   risks     dependencies   max 3 files
      요구사항    식별       매핑          per task
```

### 2. Implementation
- 한 번에 하나의 atomic task만 수행
- 각 task 완료 시 즉시 검증
- HANDOFF.md 업데이트로 상태 보존

### 3. Post-Implementation
- 결과 vs 예측 비교 → 메트릭 기록
- 패턴 학습 → 템플릿 개선

## Delegation Matrix

| 작업 유형 | 위임 대상 | 조건 |
|----------|-----------|------|
| Deep reasoning | `oracle` agent | 아키텍처, 복잡한 결정 |
| Evidence research | `librarian` agent | 검증 필요한 주장 |
| Large analysis | Gemini CLI | 200K+ tokens |
| Rapid prototype | Codex CLI | 보일러플레이트 |
| 일반 구현 | Native Task | 기본 케이스 |

## Quality Gates

각 도구 사용 후 자동 검증:
- [ ] Lint/Type check passed
- [ ] Tests green (or documented pre-existing failures)
- [ ] No security vulnerabilities introduced
- [ ] Changes match spec

## Magic Keywords

| 키워드 | 동작 |
|-------|------|
| `spec:` | Pre-implementation 스펙 세분화 시작 |
| `gemini:` | Gemini CLI로 대규모 분석 위임 |
| `evidence:` | Librarian agent로 증거 수집 |
| `deep:` | Oracle agent로 심층 분석 |

## File References

- @agents/oracle.md - Deep reasoning specialist
- @agents/librarian.md - Evidence-based research
- @templates/HANDOFF.md - Session continuity
