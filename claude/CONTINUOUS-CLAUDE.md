# CONTINUOUS-CLAUDE.md - 24시간 연속 작동 Claude 시스템

> "AI의 오류가 발생해도 전체 시스템이 계속 진화하도록 설계"
>
> — Anand Chowdhary, Continuous Claude 창시자

Claude를 무한 루프로 실행하여 복잡한 작업을 자동으로 완료하는 시스템입니다.

## Core Philosophy

```yaml
principles:
  relay_race: "릴레이 경주처럼 바톤을 넘기는 방식"
  single_progress: "한 번에 하나의 의미 있는 진전"
  external_memory: "HANDOFF.md로 컨텍스트 드리프트 방지"
  trust_rules: "AI를 믿지 말고 저장소 규칙을 믿어라"
  wasteful_but_effective: "낭비적이지만 효과적인 접근법"
```

## Quick Start

### 1. 기본 연속 실행

```bash
# 테스트 커버리지 증가
./scripts/continuous-claude.sh "테스트 커버리지를 80%까지 높여주세요" --max-runs 10

# 또는 Claude Code 내에서
/continuous "테스트 커버리지를 80%까지 높여주세요" --max-runs 10
```

### 2. PR 기반 안전한 자동화

```bash
# CI 통과 시 자동 병합
./scripts/continuous-claude.sh "의존성 업그레이드" --pr-loop --auto-merge

# CI 실패해도 PR 유지 (리뷰용)
./scripts/continuous-claude.sh "리팩토링" --pr-loop --no-discard
```

### 3. 시간/비용 제한

```bash
# 2시간 동안 최대 $15까지
./scripts/continuous-claude.sh "기술 부채 해결" --max-duration 2h --max-cost 15
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CONTINUOUS CLAUDE SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │   HANDOFF   │◄───►│   CLAUDE    │◄───►│    HOOKS    │               │
│  │    .md      │     │    CODE     │     │             │               │
│  │  (Memory)   │     │  (Engine)   │     │ continuous  │               │
│  └──────┬──────┘     └──────┬──────┘     │   -loop.py  │               │
│         │                   │            │ ralph-loop  │               │
│         │                   │            │    .py      │               │
│         ▼                   ▼            └──────┬──────┘               │
│  ┌─────────────┐     ┌─────────────┐            │                      │
│  │   LOG       │     │    GIT      │◄───────────┘                      │
│  │  .md        │     │  + CI/CD    │                                   │
│  │ (History)   │     │  (Safety)   │                                   │
│  └─────────────┘     └─────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Execution Flow

```
┌───────────────────────────────────────────────────────────────────────┐
│                          CONTINUOUS LOOP                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   Run 1          Run 2          Run 3          Run N                  │
│  ┌─────┐        ┌─────┐        ┌─────┐        ┌─────┐                 │
│  │     │───────►│     │───────►│     │───────►│     │                 │
│  │  A  │        │  B  │        │  C  │        │  ✓  │                 │
│  │     │        │     │        │     │        │     │                 │
│  └──┬──┘        └──┬──┘        └──┬──┘        └─────┘                 │
│     │              │              │                                    │
│     ▼              ▼              ▼                                    │
│  HANDOFF        HANDOFF        HANDOFF       COMPLETE                 │
│  (바톤 전달)    (바톤 전달)    (바톤 전달)   (목표 달성)              │
│                                                                        │
│  "한 번에 하나의 의미 있는 진전만 만들고 바톤을 넘긴다"               │
│                                                                        │
└───────────────────────────────────────────────────────────────────────┘
```

## External Memory System (HANDOFF.md)

### Purpose

- **Context Preservation**: 각 실행 간 상태를 보존
- **Context Drift Prevention**: 컨텍스트 윈도우 제한 극복
- **Self-Improvement**: 반복이 쌓이면서 자기 개선
- **Clean Handoff**: 긴 로그 대신 깔끔한 인수인계

### Structure

```markdown
# Continuous Claude Handoff

## Current Goal
[목표 및 완료 기준]

## Completed in This Run
- [이번 실행에서 완료된 작업들]

## Next Steps for Next Run
1. [다음 실행에서 해야 할 작업 - 우선순위 순]

## Blockers & Notes
- [주의할 점, 발견된 이슈]

## Progress Metrics
| Run # | Files Modified | Tests Added |

## Status
`CONTINUING` or `CONTINUOUS_COMPLETE`
```

### Best Practices

```yaml
do:
  - "깔끔한 인수인계 패키지 작성"
  - "다음 단계를 명확하게 기록"
  - "발견된 이슈 즉시 기록"
  - "완료 기준 체크리스트 유지"

dont:
  - "긴 로그 작성 ❌"
  - "모든 시도 기록 ❌"
  - "디버그 정보 과다 포함 ❌"
```

## PR Loop (Safe Mode)

### Philosophy

> "AI를 믿지 말고 저장소 규칙을 믿어라"

기존 GitHub 워크플로우(코드 리뷰, 필수 CI)를 활용하여 운영 리스크를 최소화합니다.

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      PR LOOP WORKFLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. Branch      2. Claude      3. Create      4. Wait CI      │
│   ┌───────┐      ┌───────┐      ┌───────┐      ┌───────┐       │
│   │Create │─────►│Execute│─────►│  PR   │─────►│Checks │       │
│   │Branch │      │ Task  │      │       │      │       │       │
│   └───────┘      └───────┘      └───────┘      └───┬───┘       │
│                                                     │           │
│                                           ┌─────────┴─────────┐ │
│                                           ▼                   ▼ │
│                                      ┌───────┐           ┌───────┐
│                                      │ PASS  │           │ FAIL  │
│                                      │ Merge │           │Discard│
│                                      └───┬───┘           └───┬───┘
│                                          │                   │   │
│                                          └─────────┬─────────┘   │
│                                                    ▼             │
│                                              ┌───────────┐       │
│                                              │  Update   │       │
│                                              │   Main    │───────┤
│                                              └───────────┘       │
│                                                    │             │
│                                                    └─── LOOP ────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Safety Features

```yaml
branch_isolation:
  - "각 실행마다 새 브랜치 생성"
  - "main 브랜치 직접 수정 금지"
  - "실패 시 브랜치 삭제"

ci_verification:
  - "PR 생성 후 CI 통과 대기"
  - "모든 체크 통과 시에만 병합"
  - "실패 시 자동 폐기 또는 리뷰용 유지"

rollback_capability:
  - "각 PR은 독립적"
  - "문제 발생 시 개별 revert 가능"
  - "git 히스토리로 전체 추적 가능"
```

## Completion Signal System

### Signal Types

```yaml
completion_signals:
  - "CONTINUOUS_COMPLETE"
  - "CONTINUOUS_CLAUDE_PROJECT_COMPLETE"
  - "[LOOP_COMPLETE]"
  - "[CONTINUOUS_DONE]"

threshold:
  default: 3  # 연속 3회 신호 시 완료
  configurable: true
```

### Signal Flow

```
Claude Output ──► Hook Check ──► Signal Detected?
                      │                │
                      │           Yes  │  No
                      │                │
                      ▼                ▼
              Count++            Continue
                      │
                      ▼
              Threshold Reached?
                      │
               Yes    │   No
                      │
                ▼     │     ▼
             STOP     │  Continue
```

## Integration with Context Engineering

### Hook Configuration

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python ~/.claude/hooks/continuous-loop.py",
        "timeout": 10
      }
    ],
    "SubagentStop": [
      {
        "type": "command",
        "command": "python ~/.claude/hooks/continuation-enforcer.py",
        "timeout": 5
      }
    ]
  }
}
```

### Magic Keyword Support

```yaml
keywords:
  - continuous
  - loop
  - 연속
  - 루프

activation:
  "continuous: <task>" → /continuous <task>
  "루프: <task>" → /continuous <task>
```

### Related Commands

| Command | Integration |
|---------|-------------|
| `/verify-app` | 각 반복 후 검증 |
| `/commit-push-pr` | PR 생성 |
| `/research` | 정보 수집 단계 |

## Use Cases

### 1. 테스트 커버리지 증가

```bash
./scripts/continuous-claude.sh "src/ 디렉토리의 테스트 커버리지를 80%까지 높여주세요. \
한 번에 하나의 파일만 처리하고, 가장 커버리지가 낮은 파일부터 시작하세요." \
--max-runs 30 --max-cost 20
```

**예상 결과**: 주말 동안 20개의 테스트 파일 추가

### 2. 의존성 업그레이드

```bash
./scripts/continuous-claude.sh "package.json의 outdated 의존성을 하나씩 업그레이드하세요. \
각 업그레이드마다 테스트를 실행하고, 호환성 문제가 있으면 해결하세요." \
--pr-loop --auto-merge
```

**예상 결과**: CI 검증된 안전한 업그레이드

### 3. 기술 부채 해결

```bash
./scripts/continuous-claude.sh "코드베이스의 TODO 주석을 하나씩 해결하세요. \
각 TODO를 해결한 후 관련 테스트를 추가하세요." \
--max-duration 4h
```

**예상 결과**: 점진적인 기술 부채 감소

### 4. 대규모 마이그레이션

```bash
./scripts/continuous-claude.sh "React 클래스 컴포넌트를 함수형 컴포넌트로 마이그레이션하세요. \
한 번에 하나의 컴포넌트만 처리하세요." \
--pr-loop --branch-prefix migrate/
```

**예상 결과**: 리뷰 가능한 개별 PR들

### 5. Dependabot 확장

```bash
./scripts/continuous-claude.sh "Dependabot PR을 확인하고, 릴리스 노트를 참고하여 \
호환성 문제가 있는 경우 코드를 수정하세요." \
--pr-loop --auto-merge
```

**예상 결과**: 자동 의존성 업데이트 + 호환성 수정

## Configuration

### Script Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-runs` | 10 | 최대 반복 횟수 |
| `--max-cost` | 10 | 최대 비용 (USD) |
| `--max-duration` | 1h | 최대 실행 시간 |
| `--sleep` | 5 | 반복 간 대기 (초) |
| `--completion-signal` | CONTINUOUS_COMPLETE | 완료 신호 |
| `--completion-threshold` | 3 | 완료 신호 횟수 |
| `--pr-loop` | false | PR 안전 모드 |
| `--auto-merge` | false | 자동 병합 |
| `--handoff-file` | .claude/HANDOFF.md | 외부 메모리 경로 |

### Environment Variables

```bash
# 프로젝트 디렉토리 지정
export CLAUDE_PROJECT_DIR=/path/to/project

# 커스텀 HANDOFF 파일
export CONTINUOUS_HANDOFF_FILE=/custom/path/HANDOFF.md
```

## Monitoring & Logs

### Log Locations

```
.claude/
├── HANDOFF.md           # 현재 인수인계 상태
├── continuous-log.md    # 전체 실행 로그
└── continuous-runs/     # 각 실행별 상세 로그
    ├── run-001.md
    ├── run-002.md
    └── ...
```

### Progress Monitoring

```bash
# 현재 상태
cat .claude/HANDOFF.md

# 실행 로그
tail -f .claude/continuous-log.md

# 비용 추적
grep -r "cost\|token" .claude/continuous-runs/
```

## Safety & Cost Management

### Cost Controls

```yaml
cost_management:
  max_cost_default: $10
  warning_at: 80%
  hard_stop: true

recommendations:
  small_task: "--max-cost 5"
  medium_task: "--max-cost 15"
  large_task: "--max-cost 30"
```

### Failure Recovery

```yaml
failure_handling:
  max_consecutive_failures: 3

  on_failure:
    1: "마지막 정상 상태로 롤백"
    2: "실패 내용 HANDOFF.md에 기록"
    3: "다음 실행에서 범위 축소"

  recovery_strategies:
    - "실패한 파일 건너뛰기"
    - "더 작은 단위로 분할"
    - "대안적 접근법 시도"
```

### Git Safety

```yaml
git_safety:
  always_create_branch: true
  never_force_push: true
  never_modify_main_directly: true
  require_ci_pass: true  # PR 모드
  preserve_history: true
```

## Ralph Wiggum Technique Integration

이 시스템은 [Ralph Wiggum Technique](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)와 호환됩니다:

```yaml
ralph_integration:
  stop_hook: "continuous-loop.py + ralph-loop.py"
  safe_word: "CONTINUOUS_COMPLETE"
  blocking_behavior: "완료 신호 없이 종료 차단"
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| 무한 루프 | `--max-runs` 또는 `--max-duration` 설정 |
| 비용 초과 | `--max-cost` 설정 |
| CI 계속 실패 | `--no-discard`로 리뷰 후 수동 수정 |
| 진행 없음 | HANDOFF.md의 다음 단계 명확화 |
| 컨텍스트 드리프트 | HANDOFF.md 정리 및 목표 재확인 |

### Debug Mode

```bash
# 상세 로그
./scripts/continuous-claude.sh "task" --verbose

# 실제 실행 없이 테스트
./scripts/continuous-claude.sh "task" --dry-run
```

## References

- [Running Claude Code in a loop](https://anandchowdhary.com/blog/2025/running-claude-code-in-a-loop) - Anand Chowdhary
- [Continuous Claude GitHub](https://github.com/AnandChowdhary/continuous-claude)
- [Ralph Wiggum Technique](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
