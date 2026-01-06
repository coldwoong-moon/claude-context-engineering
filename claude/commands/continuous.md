# /continuous - Continuous Claude Loop Execution

연속 루프 기반 작업 실행 시스템입니다. Claude를 무한 루프로 실행하여 복잡한 작업을 자동으로 완료합니다.

## Core Concept

```yaml
philosophy:
  - "릴레이 경주처럼 바톤을 넘기는 방식"
  - "한 번에 하나의 의미 있는 진전"
  - "외부 메모리로 컨텍스트 드리프트 방지"
  - "AI를 믿지 말고 저장소 규칙을 믿어라"
```

## Usage

### 1. 기본 연속 실행
```bash
# 테스트 커버리지 증가
/continuous "테스트 커버리지를 80%까지 높여주세요" --max-runs 10

# 기술 부채 해결
/continuous "TODO 주석을 하나씩 해결하세요" --max-cost 5

# 리팩토링
/continuous "코드 중복을 제거하세요" --max-duration 2h
```

### 2. PR 루프 모드 (안전한 자동화)
```bash
# PR 기반 안전한 자동화
/continuous "마이그레이션 작업" --pr-loop --auto-merge

# CI 실패 시 자동 폐기
/continuous "의존성 업그레이드" --pr-loop --discard-on-failure
```

### 3. 외부 메모리 활용
```bash
# HANDOFF.md를 통한 상태 전달
/continuous "시스템 개선" --handoff-file .claude/HANDOFF.md
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `$TASK` | 반복 실행할 작업 설명 (필수) | - |
| `--max-runs N` | 최대 반복 횟수 | 10 |
| `--max-cost N` | 최대 비용 (USD) | 10 |
| `--max-duration T` | 최대 실행 시간 (예: 2h, 30m) | 1h |
| `--pr-loop` | PR 기반 안전 모드 활성화 | false |
| `--auto-merge` | CI 통과 시 자동 병합 | false |
| `--discard-on-failure` | CI 실패 시 PR 폐기 | true |
| `--handoff-file PATH` | 외부 메모리 파일 경로 | .claude/HANDOFF.md |
| `--completion-signal` | 완료 신호 문자열 | CONTINUOUS_COMPLETE |
| `--sleep N` | 반복 간 대기 시간 (초) | 5 |
| `--branch-prefix` | PR 브랜치 접두사 | continuous-claude/ |

## Execution Flow

### Standard Loop
```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS CLAUDE LOOP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │  START   │───→│ HANDOFF  │───→│ EXECUTE  │───→│ VERIFY   │  │
│   └──────────┘    │  READ    │    │  TASK    │    │ PROGRESS │  │
│                   └──────────┘    └──────────┘    └────┬─────┘  │
│                        ↑                               │        │
│                        │       ┌──────────────────────┘        │
│                        │       ↓                               │
│                   ┌──────────┐    ┌──────────┐                 │
│                   │ HANDOFF  │←───│ COMPLETE │──→ DONE?        │
│                   │  WRITE   │    │  CHECK   │     │           │
│                   └──────────┘    └──────────┘     ↓           │
│                        │                         YES → EXIT    │
│                        └───────── NO ──────────────────────────┤
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### PR Loop (Safe Mode)
```
┌─────────────────────────────────────────────────────────────────┐
│                      PR LOOP (SAFE MODE)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │  CREATE  │───→│  CLAUDE  │───→│  CREATE  │───→│ WAIT CI  │  │
│   │  BRANCH  │    │  EXECUTE │    │   PR     │    │  CHECK   │  │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘  │
│                                                        │        │
│                   ┌────────────────────────────────────┘        │
│                   ↓                                             │
│              ┌────────────┐                                     │
│              │  CI PASS?  │                                     │
│              └─────┬──────┘                                     │
│                    │                                            │
│         ┌─────────┴─────────┐                                   │
│         ↓                   ↓                                   │
│    ┌─────────┐         ┌─────────┐                              │
│    │  MERGE  │         │ DISCARD │                              │
│    │   PR    │         │   PR    │                              │
│    └────┬────┘         └────┬────┘                              │
│         │                   │                                   │
│         └─────────┬─────────┘                                   │
│                   ↓                                             │
│            ┌─────────────┐                                      │
│            │ UPDATE MAIN │───→ LOOP                             │
│            └─────────────┘                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## HANDOFF.md Template

연속 실행 간 상태를 전달하는 외부 메모리 파일입니다:

```markdown
# Continuous Claude Handoff

## 🎯 Current Goal
[현재 목표 - 루프 시작 시 설정]

## ✅ Completed in This Run
- [이번 실행에서 완료된 작업 1]
- [이번 실행에서 완료된 작업 2]

## 🔄 In Progress
- [현재 진행 중인 작업]
- [발견된 이슈 및 해결 시도]

## 📋 Next Steps for Next Run
1. [다음 실행에서 해야 할 작업 1]
2. [다음 실행에서 해야 할 작업 2]

## ⚠️ Blockers & Notes
- [주의할 점 또는 차단 요소]

## 📊 Progress Metrics
- **Run #**: [현재 반복 횟수]
- **Started**: [시작 시간]
- **Files Modified**: [수정된 파일 수]
- **Tests Added**: [추가된 테스트 수]

## 🏁 Completion Check
- [ ] 목표 달성 여부: [YES/NO]
- [ ] 완료 신호: [CONTINUOUS_COMPLETE 또는 계속]
```

## Prompting Guidelines

### 효과적인 프롬프트 패턴

```yaml
good_prompts:
  - "한 번에 하나의 테스트 파일만 추가하고, 다음 파일을 HANDOFF.md에 기록"
  - "가장 커버리지가 낮은 파일을 찾아 테스트 추가"
  - "TODO 주석을 하나 해결하고 다음 TODO를 메모"

bad_prompts:
  - "모든 테스트를 작성해" (너무 광범위)
  - "완벽하게 리팩토링해" (완료 기준 모호)
  - "버그를 모두 수정해" (범위 불명확)
```

### 프롬프트 템플릿

```markdown
## Continuous Claude Instructions

당신은 연속 개발 루프의 일부입니다.

**핵심 규칙**:
1. 한 번에 하나의 의미 있는 진전만 만드세요
2. 긴 로그 대신 깔끔한 인수인계 패키지를 작성하세요
3. HANDOFF.md를 릴레이 바톤처럼 사용하세요
4. 완료되면 CONTINUOUS_COMPLETE를 출력하세요

**현재 목표**: $TASK

**이전 실행에서의 메모**:
[HANDOFF.md 내용]

**당신의 임무**:
1. HANDOFF.md에서 이전 진행 상황 확인
2. 다음 단계 하나만 완료
3. 진행 상황과 다음 단계를 HANDOFF.md에 기록
4. 모든 목표 달성 시 CONTINUOUS_COMPLETE 출력
```

## Integration with Context Engineering

### Hook 연동

```yaml
hooks:
  Stop:
    - continuous-loop.py  # 완료 신호 확인 및 HANDOFF 업데이트
    - ralph-loop.py       # 기존 Ralph Loop와 통합

  SubagentStop:
    - continuation-enforcer.py  # 미완료 작업 시 계속 진행
```

### Magic Keyword 지원

```bash
# 매직 키워드로 활성화
continuous: <task>
loop: <task>
연속: <task>
루프: <task>
```

## Safety Features

### 비용 관리
```yaml
cost_controls:
  max_cost_default: 10  # USD
  warning_threshold: 0.8  # 80%에서 경고
  hard_stop: true  # 한도 초과 시 강제 중단
```

### 실패 복구
```yaml
failure_handling:
  max_consecutive_failures: 3
  on_failure:
    - revert_to_last_good_state
    - document_failure_in_handoff
    - reduce_scope_for_next_run
```

### Git 안전장치
```yaml
git_safety:
  always_create_branch: true
  never_force_push: true
  require_ci_pass: true  # PR 모드
  auto_revert_on_failure: true
```

## Examples

### 테스트 커버리지 증가
```bash
/continuous "src/ 디렉토리의 테스트 커버리지를 80%까지 높여주세요. \
한 번에 하나의 파일만 처리하고, 가장 커버리지가 낮은 파일부터 시작하세요." \
--max-runs 20 --max-cost 15
```

### 의존성 업그레이드 (PR 모드)
```bash
/continuous "package.json의 outdated 의존성을 하나씩 업그레이드하세요. \
각 업그레이드마다 테스트를 실행하고, 실패하면 롤백하세요." \
--pr-loop --auto-merge
```

### 기술 부채 해결
```bash
/continuous "코드베이스의 TODO 주석을 하나씩 해결하세요. \
각 TODO를 해결한 후 관련 테스트를 추가하세요." \
--max-duration 2h --handoff-file .claude/tech-debt-handoff.md
```

### 대규모 마이그레이션
```bash
/continuous "React 클래스 컴포넌트를 함수형 컴포넌트로 마이그레이션하세요. \
한 번에 하나의 컴포넌트만 처리하세요." \
--pr-loop --branch-prefix migrate/
```

## Monitoring & Logs

### 실행 로그 위치
```
.claude/
├── HANDOFF.md           # 현재 인수인계 상태
├── continuous-log.md    # 전체 실행 로그
└── continuous-runs/     # 각 실행별 상세 로그
    ├── run-001.md
    ├── run-002.md
    └── ...
```

### 진행 상황 확인
```bash
# 현재 상태 확인
cat .claude/HANDOFF.md

# 실행 로그 확인
cat .claude/continuous-log.md

# 비용 추적
grep "cost" .claude/continuous-runs/*.md
```

## Related Commands

- `/verify-app` - 앱 검증 (lint, test, build)
- `/commit-push-pr` - Git 워크플로우
- `/research` - 연구 모드

## References

- [Running Claude Code in a loop](https://anandchowdhary.com/blog/2025/running-claude-code-in-a-loop)
- [Continuous Claude GitHub](https://github.com/AnandChowdhary/continuous-claude)
- [Ralph Wiggum Technique](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)
