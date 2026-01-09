---
name: moon-loop
description: 목표 달성까지 자율 연속 실행 (Ralph + Continuous + TDD 통합)
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite, Task, WebSearch, WebFetch
model: sonnet
context: fork
agent: general-purpose
argument-hint: <goal> [--mode continuous|ralph|tdd] [--max N] [--verify CMD]
hooks:
  PreToolUse:
    - matcher: "Bash"
      command: "python3 ~/.claude/hooks/loop-safety-check.py"
  PostToolUse:
    - matcher: "Edit|Write"
      command: "python3 ~/.claude/hooks/loop-progress-update.py"
  Stop:
    - command: "python3 ~/.claude/hooks/unified-loop.py"
---

# /moon-loop - Unified Autonomous Loop System

> Ralph Wiggum + Continuous Claude + TDD를 통합한 자율 루프 시스템

## Quick Start

```bash
# 기본 연속 실행
/moon-loop "테스트 커버리지 80% 달성"

# TDD 모드
/moon-loop "API 엔드포인트 구현" --mode tdd --verify "npm test"

# Continuous 모드 (HANDOFF.md 기반)
/moon-loop "대규모 리팩토링" --mode continuous --max 30

# PR 안전 모드
/moon-loop "의존성 업그레이드" --pr-loop --auto-merge
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$GOAL` | 달성할 목표 (필수) | - |
| `--mode` | 실행 모드 (continuous/ralph/tdd/auto) | auto |
| `--max N` | 최대 반복 횟수 | 10 |
| `--verify CMD` | 각 단계 후 검증 명령 | - |
| `--pr-loop` | PR 기반 안전 모드 | false |
| `--auto-merge` | CI 통과 시 자동 병합 | false |
| `--timeout M` | 타임아웃 (분) | 60 |
| `--cost N` | 최대 비용 (USD) | 10 |

## Execution Modes

### Auto Mode (default)
목표와 컨텍스트를 분석하여 최적 모드 자동 선택:
- 테스트 키워드 → TDD 모드
- 리팩토링/마이그레이션 → Continuous 모드
- 버그 수정/작은 작업 → Ralph 모드

### Continuous Mode
HANDOFF.md를 통한 릴레이 방식 연속 실행:
```yaml
philosophy:
  - "릴레이 경주처럼 바톤을 넘기는 방식"
  - "한 번에 하나의 의미 있는 진전"
  - "외부 메모리로 컨텍스트 드리프트 방지"
```

### Ralph Mode
Stop Hook 기반 자율 실행:
```yaml
philosophy:
  - "완료 조건 충족까지 계속 실행"
  - "todo.md로 진행 상황 추적"
  - "실패 시 자동 재시도"
```

### TDD Mode
테스트 주도 개발 사이클:
```yaml
cycle:
  1_red: "실패하는 테스트 작성"
  2_green: "테스트 통과 최소 코드"
  3_refactor: "코드 개선"
```

## Loop Protocol

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MOON LOOP EXECUTION                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│   │  INIT    │───→│  STATE   │───→│ EXECUTE  │───→│  VERIFY  │          │
│   │  GOAL    │    │  READ    │    │   STEP   │    │  RESULT  │          │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘          │
│                        ↑                               │                 │
│                        │       ┌──────────────────────┘                 │
│                        │       ↓                                        │
│                   ┌──────────┐    ┌──────────┐                          │
│                   │  STATE   │←───│ COMPLETE │──→ DONE?                 │
│                   │  WRITE   │    │  CHECK   │     │                    │
│                   └──────────┘    └──────────┘     ↓                    │
│                        │                         YES → MOON_COMPLETE    │
│                        └───────── NO ────────────────→ CONTINUE         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## State Management

### HANDOFF.md (External Memory)
```markdown
# Moon Loop Handoff

## 🎯 Goal
[목표 및 완료 기준]

## ✅ Completed This Run
- [완료된 작업들]

## 🔄 Current State
- Run #: N
- Mode: [continuous|ralph|tdd]
- Last Result: [pass|fail]

## 📋 Next Steps
1. [다음 작업]

## ⚠️ Notes
- [주의사항]
```

### Completion Signals
```yaml
signals:
  - "MOON_COMPLETE"      # 기본 완료 신호
  - "LOOP_COMPLETE"      # 대체 신호
  - "[DONE]"             # 간단 신호
  - "목표 달성"           # 한글 신호
```

## Multi-AI Integration

대규모 작업 시 자동 위임:

| 상황 | 위임 대상 | 트리거 |
|------|-----------|--------|
| 50+ 파일 분석 | Gemini CLI | `gemini -p "..." -f "src/**/*"` |
| 보일러플레이트 생성 | Codex CLI | `codex "..."` |
| 복잡한 추론 | Claude (continue) | 기본 |

## Safety Features

```yaml
safety:
  max_iterations: 10
  max_consecutive_failures: 3
  timeout_minutes: 60
  cost_limit_usd: 10

  on_failure:
    retry: "동일 작업 재시도 (max 3)"
    skip: "건너뛰고 다음으로"
    stop: "중단하고 상태 저장"

  git_safety:
    always_create_branch: true
    never_force_push: true
    require_ci_pass: true  # PR 모드
```

## Examples

### 테스트 커버리지 증가
```bash
/moon-loop "src/ 테스트 커버리지 80% 달성. 가장 낮은 파일부터." \
  --mode tdd --verify "npm test -- --coverage" --max 30
```

### 대규모 마이그레이션
```bash
/moon-loop "React 클래스 → 함수형 컴포넌트 마이그레이션" \
  --mode continuous --pr-loop --max 50
```

### 기술 부채 해결
```bash
/moon-loop "TODO 주석 하나씩 해결" \
  --mode ralph --max 20 --cost 15
```

## Cancellation

루프 중단:
```bash
/moon-cancel            # 명령으로 취소
# 또는 Ctrl+C
# 또는 MOON_CANCEL 출력
```

## Related Commands

- `/moon-research` - 심층 연구
- `/moon-review` - 코드 리뷰
- `/moon-cancel` - 루프 취소
- `/verify-app` - 앱 검증

---

## Execution Start

**Goal**: $ARGUMENTS

### Loop Rules

1. **한 번에 하나의 진전**: 작은 단위로 작업하고 검증
2. **상태 기록**: `.claude/HANDOFF.md`에 진행 상황 저장
3. **완료 신호**: 목표 달성 시 `MOON_COMPLETE` 출력
4. **검증 필수**: 각 단계 후 테스트/린트 실행

### Starting Work

현재 상태를 확인하고 작업을 시작합니다:

1. `.claude/HANDOFF.md` 상태 확인
2. 미완료 작업 식별
3. 다음 단계 실행
4. 결과 검증 및 상태 업데이트
5. 완료 시 `MOON_COMPLETE` 출력

```
작업을 시작합니다. 완료되면 MOON_COMPLETE를 출력하겠습니다.
```
