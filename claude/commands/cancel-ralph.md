# /cancel-ralph - Ralph Loop 취소

현재 실행 중인 Ralph Loop를 안전하게 취소합니다.

## Usage

```bash
# 기본 취소
/cancel-ralph

# 상태 저장 후 취소
/cancel-ralph --save-state

# 즉시 취소 (상태 저장 안함)
/cancel-ralph --force
```

## What This Does

1. **상태 파일 업데이트**: `.claude/ralph-status.json`에 취소 상태 기록
2. **todo.md 업데이트**: 현재 진행 중인 작업에 취소 표시
3. **HANDOFF.md 업데이트**: 취소 시점의 상태 저장
4. **Stop Hook 비활성화**: Ralph Loop의 continuation 중단

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--save-state` | 현재 상태를 HANDOFF.md에 저장 | true |
| `--force` | 즉시 취소 (상태 저장 안함) | false |
| `--reason TEXT` | 취소 사유 기록 | "사용자 요청" |

## Execution

이 명령어를 실행하면:

```yaml
actions:
  1_update_status:
    file: ".claude/ralph-status.json"
    set:
      status: "cancelled"
      cancelledAt: "현재 시간"
      reason: "사용자 요청"

  2_update_todo:
    file: ".claude/todo.md"
    add: "- [!] RALPH_CANCEL: 사용자 요청으로 루프 취소됨"

  3_save_handoff:
    condition: "--save-state"
    file: ".claude/HANDOFF.md"
    update:
      - "취소 시점 반복 횟수"
      - "완료된 작업 목록"
      - "미완료 작업 목록"

  4_output:
    message: "RALPH_CANCELLED"
```

## After Cancellation

취소 후 다시 시작하려면:

```bash
# 이전 상태에서 재개
/ralph-loop "이전 작업 계속" --resume

# 새로 시작
/ralph-loop "새 작업" --max-iterations 20
```

## Related

- `/ralph-loop` - Ralph Loop 시작
- `/continuous` - Continuous Claude 루프
