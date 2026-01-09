---
name: moon-cancel
description: 진행 중인 Moon Loop 취소
allowed-tools: Bash, Read, Write
---

# /moon-cancel - Moon Loop Cancellation

진행 중인 Moon Loop를 안전하게 취소합니다.

## Usage

```bash
/moon-cancel              # 현재 루프 취소
/moon-cancel --save       # 상태 저장 후 취소
/moon-cancel --rollback   # 마지막 체크포인트로 롤백
```

## Cancellation Protocol

```yaml
steps:
  1_signal:
    action: "MOON_CANCEL 신호 전송"
    result: "루프 중단 요청"

  2_save_state:
    action: "현재 상태 HANDOFF.md에 저장"
    includes:
      - completed_tasks
      - current_progress
      - next_steps

  3_cleanup:
    action: "임시 파일 정리"
    preserves:
      - source_changes
      - test_results
      - logs

  4_report:
    action: "중단 보고서 생성"
    location: ".claude/moon-cancel-report.md"
```

## Options

| Option | Description |
|--------|-------------|
| `--save` | 현재 진행 상태 저장 (재개 가능) |
| `--rollback` | 마지막 성공 체크포인트로 롤백 |
| `--force` | 강제 종료 (상태 저장 없음) |

## Execution

현재 Moon Loop를 취소합니다:

1. 진행 중인 작업 확인
2. 상태 저장 (--save 옵션 시)
3. 루프 종료 신호 전송
4. 정리 및 보고서 생성

```
MOON_CANCEL

루프가 취소되었습니다. 상태가 .claude/HANDOFF.md에 저장되었습니다.
```
