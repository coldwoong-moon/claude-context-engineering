# /ralph-loop - Ralph Wiggum Autonomous Loop System

> "AI의 오류가 발생해도 전체 시스템이 계속 진화하도록 설계"
>
> Ralph Wiggum 기법은 Stop Hook을 사용하여 명시적 완료 조건이 충족될 때까지
> Claude가 자율적으로 작업을 계속하도록 합니다.

## Quick Start

```bash
# 기본 사용법
/ralph-loop "테스트 커버리지를 80%까지 높여주세요"

# 최대 반복 횟수 제한 (중요!)
/ralph-loop "TODO 주석 해결" --max-iterations 20

# TDD 모드
/ralph-loop "새 기능 구현" --tdd --run-tests "npm test"

# 검증 명령 포함
/ralph-loop "리팩토링" --verify "npm run lint && npm test"
```

## Core Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RALPH WIGGUM LOOP PATTERN                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│   │  START   │───→│  EXECUTE │───→│  VERIFY  │───→│  CHECK   │      │
│   │  TASK    │    │   STEP   │    │  TESTS   │    │ COMPLETE │      │
│   └──────────┘    └──────────┘    └────┬─────┘    └────┬─────┘      │
│                        ↑               │               │             │
│                        │          PASS │          NO   │ YES         │
│                        │               ▼               ▼             │
│                   ┌────────────┐  ┌────────┐     ┌────────┐          │
│                   │   FIX &    │←─│ FAILED │     │  DONE  │          │
│                   │   RETRY    │  └────────┘     │ RALPH! │          │
│                   └────────────┘                 └────────┘          │
│                        │                                             │
│                        └─────────── CONTINUE ────────────────────────┤
│                                                                      │
│   💡 "Stop Hook이 종료를 가로채서 완료될 때까지 계속 실행"            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TASK` | 실행할 작업 설명 (필수) | - |
| `--max-iterations N` | **필수** - 최대 반복 횟수 | 10 |
| `--safe-word WORD` | 완료 신호 단어 | RALPH_COMPLETE |
| `--tdd` | TDD 모드 활성화 | false |
| `--run-tests CMD` | 테스트 실행 명령 | npm test |
| `--verify CMD` | 각 단계 후 검증 명령 | - |
| `--on-fail ACTION` | 실패 시 행동 (retry/skip/stop) | retry |
| `--max-retries N` | 실패 시 최대 재시도 횟수 | 3 |
| `--timeout MINUTES` | 전체 타임아웃 (분) | 60 |
| `--verbose` | 상세 로그 출력 | false |

## Usage Modes

### 1. Basic Loop Mode

```bash
/ralph-loop "src/ 디렉토리의 모든 파일에 JSDoc 추가" --max-iterations 30
```

작업 완료 시 `RALPH_COMPLETE` 출력으로 종료.

### 2. TDD Mode (Test-Driven Development)

```bash
/ralph-loop "사용자 인증 기능 구현" --tdd --run-tests "npm test" --max-iterations 25
```

TDD 사이클:
1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트 통과하는 최소 코드 작성
3. **Refactor**: 코드 개선

### 3. Verification Mode

```bash
/ralph-loop "TypeScript 마이그레이션" \
  --verify "npm run typecheck && npm run lint" \
  --max-iterations 50
```

각 단계 후 검증 명령 실행.

### 4. PR-Safe Mode

```bash
/ralph-loop "의존성 업그레이드" \
  --max-iterations 20 \
  --verify "npm test && npm run build" \
  --on-fail skip
```

CI와 통합하여 안전하게 실행.

## Completion Signals

```yaml
completion_signals:
  primary:
    - "RALPH_COMPLETE"      # 기본 완료 신호
    - "[RALPH_DONE]"        # 대체 형식

  custom:
    - "--safe-word"로 지정한 커스텀 신호

  automatic:
    - 모든 테스트 통과 (TDD 모드)
    - 검증 명령 성공 + todo.md 비어있음
```

## TDD Workflow

### Auto TDD Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      TDD CYCLE IN RALPH LOOP                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Iteration 1: RED                                               │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 실패하는 테스트 작성                 │                     │
│   │ 2. npm test → FAIL (expected)          │                     │
│   │ 3. todo.md에 구현 필요 항목 추가       │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Iteration 2: GREEN                                             │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 테스트 통과 최소 코드 작성           │                     │
│   │ 2. npm test → PASS                     │                     │
│   │ 3. todo.md 항목 체크                   │                     │
│   └────────────────────────────────────────┘                     │
│                      ↓                                           │
│   Iteration 3: REFACTOR                                          │
│   ┌────────────────────────────────────────┐                     │
│   │ 1. 코드 개선 (중복 제거, 명명 개선)     │                     │
│   │ 2. npm test → PASS (확인)              │                     │
│   │ 3. 다음 기능으로 이동 또는 완료         │                     │
│   └────────────────────────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### TDD Commands

```bash
# 전체 TDD 사이클
/ralph-loop "User 모델 구현" --tdd --max-iterations 15

# 특정 테스트 파일 대상
/ralph-loop "API 엔드포인트 구현" --tdd --run-tests "npm test -- api.test.ts"

# E2E 테스트 포함
/ralph-loop "로그인 페이지 구현" --tdd \
  --run-tests "npm test && npx playwright test"
```

## Integration with Hooks

### Stop Hook Integration

```python
# ~/.claude/hooks/ralph-loop.py
# Stop 이벤트 시 완료 신호 확인
# 신호 없으면 작업 계속 유도
```

### Verification Loop

```python
# ~/.claude/hooks/verification-loop.py
# 각 반복 후 테스트/린트 자동 실행
```

## Safety Features

### 무한 루프 방지

```yaml
safety_controls:
  max_iterations: 10          # 기본 최대 반복
  max_consecutive_failures: 3 # 연속 실패 제한
  timeout_minutes: 60         # 전체 타임아웃
  cost_limit_usd: 10          # 비용 제한
```

### 실패 처리 전략

```yaml
on_failure:
  retry:
    description: "동일 작업 재시도"
    max_retries: 3
    backoff: exponential

  skip:
    description: "현재 항목 건너뛰고 다음으로"
    log: true

  stop:
    description: "즉시 중단하고 상태 저장"
    save_state: true
```

## State Management

### todo.md 연동

```markdown
# Ralph Loop Todo

## In Progress
- [ ] 현재 작업 중인 항목

## Pending
- [ ] 대기 중인 항목 1
- [ ] 대기 중인 항목 2

## Completed
- [x] 완료된 항목 1 (2024-01-15)
- [x] 완료된 항목 2 (2024-01-15)
```

### HANDOFF.md 연동

Ralph Loop는 Continuous Claude의 HANDOFF.md와 통합:

```markdown
## Ralph Loop Status
- **Iteration**: 5/20
- **Safe Word**: RALPH_COMPLETE
- **Last Test Result**: PASS
- **Current Task**: API 엔드포인트 구현
```

## Examples

### 1. 테스트 커버리지 증가

```bash
/ralph-loop "커버리지가 가장 낮은 파일부터 테스트 추가. \
목표: 전체 커버리지 80%" \
--tdd --run-tests "npm test -- --coverage" \
--max-iterations 30 --timeout 120
```

### 2. 코드베이스 마이그레이션

```bash
/ralph-loop "JavaScript 파일을 TypeScript로 마이그레이션. \
한 번에 하나의 파일만 처리." \
--verify "npm run typecheck" \
--max-iterations 50 --on-fail skip
```

### 3. 버그 수정 루프

```bash
/ralph-loop "GitHub Issues에서 'bug' 라벨 이슈 해결. \
각 버그마다 테스트 추가." \
--tdd --max-iterations 20 \
--safe-word "ALL_BUGS_FIXED"
```

### 4. API 개발

```bash
/ralph-loop "REST API 엔드포인트 구현. \
OpenAPI 스펙 기반으로 TDD 방식." \
--tdd --run-tests "npm test -- api/" \
--verify "npm run lint" \
--max-iterations 25
```

### 5. 프런트엔드 개발 (Playwright)

```bash
/ralph-loop "로그인 페이지 구현 및 E2E 테스트" \
--tdd --run-tests "npm test && npx playwright test" \
--max-iterations 15
```

## Cancellation

루프를 중단하려면:

```bash
# 명령어로 취소
/cancel-ralph

# 또는 터미널에서 Ctrl+C

# 또는 todo.md에 추가:
- [!] RALPH_CANCEL: 사용자 요청으로 중단
```

## Monitoring

### 실시간 상태 확인

```bash
# 현재 반복 상태
cat .claude/ralph-status.json

# 로그 확인
tail -f .claude/ralph-loop.log

# 테스트 결과 히스토리
cat .claude/ralph-test-results.md
```

### Status File Format

```json
{
  "iteration": 5,
  "maxIterations": 20,
  "status": "running",
  "currentTask": "API 엔드포인트 구현",
  "lastTestResult": "pass",
  "consecutiveFailures": 0,
  "startTime": "2024-01-15T10:00:00Z",
  "elapsedMinutes": 15
}
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/cancel-ralph` | 현재 Ralph Loop 취소 |
| `/continuous` | Continuous Claude 루프 |
| `/verify-app` | 앱 검증 (lint, test, build) |
| `/commit-push-pr` | Git 워크플로우 |

## Best Practices

```yaml
do:
  - "항상 --max-iterations 설정"
  - "TDD 모드에서 작은 단위로 진행"
  - "검증 명령으로 품질 보장"
  - "todo.md로 진행 상황 추적"

dont:
  - "--max-iterations 없이 실행 ❌"
  - "너무 큰 작업을 한 번에 시도 ❌"
  - "테스트 없이 대규모 변경 ❌"
```

## References

- [Ralph Wiggum Plugin - Anthropic](https://github.com/anthropics/claude-code/tree/main/plugins)
- [Running Claude Code in a loop](https://anandchowdhary.com/blog/2025/running-claude-code-in-a-loop)
- [The Ralph Wiggum Technique](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)
- [Boris Journey - 30일 259 PR 사례](https://www.linkedin.com/posts/wonjun-seo-%EC%84%9C%EC%9B%90%EC%A4%80-6088a5379_github-anthropicsclaude-quickstarts-a-activity-7414289779821015040-uDhv)
