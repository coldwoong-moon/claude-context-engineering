---
description: 코드 단순화 및 정리 워크플로우
argument-hint: [@file-or-directory]
---

코드 단순화 및 정리 워크플로우

## 목적

복잡한 코드를 단순화하고 가독성을 높입니다.
Boris Cheny의 서브에이전트 패턴 적용.

## 분석 대상

```bash
# 최근 변경된 파일
git diff --name-only HEAD~5

# 복잡도가 높은 파일 (라인 수 기준)
find . -name "*.ts" -o -name "*.py" | xargs wc -l | sort -rn | head -10
```

## 단순화 원칙

### 1. 함수 분리
- 한 함수는 한 가지 일만
- 20줄 초과 시 분리 검토

### 2. 네이밍 개선
- 의도가 명확한 이름
- 축약어 지양

### 3. 중복 제거
- DRY 원칙 적용
- 공통 유틸리티 추출

### 4. 타입 명확화
- any 제거
- 유니온 타입 좁히기

### 5. 에러 처리 정리
- 일관된 에러 패턴
- 불필요한 try-catch 제거

## 출력 형식

```markdown
## 단순화 결과

### 변경된 파일
- `path/to/file.ts`: 함수 분리 (1 → 3)

### 개선 사항
1. [설명]
2. [설명]

### 메트릭
- 라인 수: 150 → 120 (-20%)
- 함수 수: 5 → 8 (+3, 더 작은 함수들)
- 복잡도: Medium → Low
```

## 사용 예시

```
/code-simplifier src/utils/parser.ts
/code-simplifier --all-recent
```
