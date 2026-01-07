---
description: 통합 에이전트 루프 - Ralph/Continuous/Research/Review 모드 통합
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
model: sonnet
---

# /loop - 통합 에이전트 루프

자율적 장기 실행 작업을 위한 통합 루프 시스템입니다.

## 사용법

```bash
# 기본 루프 (자동 모드 감지)
/loop "테스트 커버리지를 80%까지 높여주세요"

# Ralph 모드 (todo.md 기반)
/loop --mode ralph "모든 TODO 항목 해결"

# Continuous 모드 (HANDOFF.md 기반)
/loop --mode continuous "대규모 리팩토링"

# 최대 반복 설정
/loop --max 20 "의존성 업그레이드"
```

## 완료 신호

루프 완료 시 다음 신호 중 하나를 출력하세요:
- `LOOP_COMPLETE` (권장)
- `[DONE]`
- `작업완료`

## 취소 신호

루프를 중단하려면:
- `LOOP_CANCEL`
- `[CANCEL]`
- `취소`

---

## 실행 시작

**목표**: $ARGUMENTS

### 루프 규칙

1. **한 번에 하나의 진전**: 작은 단위로 작업하고 검증
2. **상태 기록**: `.claude/agent-state.json`에 진행 상황 자동 저장
3. **완료 신호**: 모든 작업 완료 시 `LOOP_COMPLETE` 출력
4. **중간 저장**: 긴 작업은 `todo.md`로 체크포인트

### 작업 시작

현재 상태를 확인하고 작업을 시작합니다:

1. `.claude/agent-state.json` 상태 확인
2. `.claude/todo.md` 미완료 작업 확인
3. 다음 작업 수행
4. 완료 시 `LOOP_COMPLETE` 출력

```
작업을 시작합니다. 완료되면 LOOP_COMPLETE를 출력하겠습니다.
```
