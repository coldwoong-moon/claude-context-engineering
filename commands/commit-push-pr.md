---
description: Git 워크플로우 자동화 (커밋 → 푸시 → PR 생성)
argument-hint: [--draft] [--no-push] [--amend]
---

Git 워크플로우 자동화: 커밋 → 푸시 → PR 생성

## 사전 정보 수집

```bash
# 현재 브랜치
BRANCH=$(git branch --show-current)

# 변경된 파일
CHANGED=$(git diff --stat HEAD)

# 최근 커밋 스타일
RECENT=$(git log --oneline -5)
```

## 실행 단계

1. **변경사항 분석**
   - `git status`로 untracked 파일 확인
   - `git diff`로 변경 내용 분석

2. **커밋 메시지 생성**
   - Conventional Commit 형식 사용
   - 변경 내용 기반 자동 생성

3. **푸시**
   - `git push -u origin $BRANCH`

4. **PR 생성**
   - `gh pr create` 사용
   - 제목: 커밋 메시지 기반
   - 본문: 변경사항 요약 + 테스트 계획

## 사용 예시

```
/commit-push-pr
```

## 옵션

- `--draft`: Draft PR 생성
- `--no-push`: 커밋만 하고 푸시하지 않음
- `--amend`: 이전 커밋 수정 (주의: force push 필요)
