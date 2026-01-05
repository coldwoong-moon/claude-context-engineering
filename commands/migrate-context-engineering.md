---
description: 프로젝트를 Context Engineering 구조로 마이그레이션
argument-hint: [--template node|python|rust|go] [--backup] [--force]
---

프로젝트를 Context Engineering 기준으로 마이그레이션하는 명령어

## 개요

현재 프로젝트에 Context Engineering 프레임워크를 설정합니다:
- `.claude/` 디렉토리 구조 생성
- Knowledge 파일 초기화
- Hook 설정 복사
- CLAUDE.md 엔트리포인트 생성

## 사전 정보 수집

```bash
# 프로젝트 루트 확인
PROJECT_ROOT=$(pwd)

# 기존 .claude 디렉토리 확인
EXISTING_CLAUDE=$(ls -la .claude 2>/dev/null)

# 프로젝트 타입 감지
PROJECT_TYPE=$(
  if [ -f "package.json" ]; then echo "node";
  elif [ -f "pyproject.toml" ]; then echo "python";
  elif [ -f "Cargo.toml" ]; then echo "rust";
  elif [ -f "go.mod" ]; then echo "go";
  else echo "generic"; fi
)
```

## 실행 단계

### 1. 디렉토리 구조 생성

```
.claude/
├── CLAUDE.md           # 엔트리포인트
├── knowledge/          # 프로젝트 지식
│   ├── context.md      # 세션 컨텍스트
│   ├── decisions.md    # 아키텍처 결정
│   ├── patterns.md     # 코드 패턴
│   └── errors.md       # 알려진 오류
├── todo.md             # 작업 목록
└── settings.local.json # 로컬 설정 (선택)
```

### 2. Knowledge 파일 초기화

각 파일에 기본 템플릿 생성:

**context.md**:
```markdown
# 프로젝트 컨텍스트

## 개요
[프로젝트 설명]

## 기술 스택
- [언어/프레임워크]

## 주요 디렉토리
- `src/` - 소스 코드
- `tests/` - 테스트

## 최근 작업
<!-- 자동 업데이트 영역 -->
```

**decisions.md**:
```markdown
# 아키텍처 결정 기록 (ADR)

## 템플릿
### [YYYY-MM-DD] 제목
- **상태**: 제안됨 | 승인됨 | 폐기됨
- **컨텍스트**: 왜 이 결정이 필요한가?
- **결정**: 무엇을 결정했는가?
- **결과**: 어떤 영향이 있는가?
```

**patterns.md**:
```markdown
# 코드 패턴

## 프로젝트 컨벤션
[코드 스타일, 네이밍 규칙 등]

## 자주 사용되는 패턴
[반복되는 코드 패턴 문서화]
```

**errors.md**:
```markdown
# 알려진 오류 및 해결책

## 알려진 해결책
| 오류 | 해결책 |
|------|--------|
| ModuleNotFoundError | `uv sync` 또는 `npm install` |
| Connection refused | `docker compose up -d` |
```

### 3. CLAUDE.md 엔트리포인트 생성

```markdown
# 프로젝트명

## 개요
[프로젝트 한 줄 설명]

## 빠른 시작
\`\`\`bash
# 의존성 설치
[패키지 매니저 명령어]

# 개발 서버 실행
[실행 명령어]

# 테스트
[테스트 명령어]
\`\`\`

## 주요 파일
- `src/` - 메인 소스 코드
- `.claude/knowledge/` - 프로젝트 지식

## Context Engineering
@.claude/knowledge/context.md
@.claude/knowledge/decisions.md
@.claude/knowledge/patterns.md
```

### 4. 로컬 설정 (선택)

`.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(git push)",
      "WebFetch(domain:github.com)"
    ]
  }
}
```

## 사용 예시

```bash
# 기본 마이그레이션
/migrate-context-engineering

# 기존 설정 백업 후 마이그레이션
/migrate-context-engineering --backup

# 특정 템플릿 사용
/migrate-context-engineering --template python

# 강제 덮어쓰기
/migrate-context-engineering --force
```

## 옵션

| 옵션 | 설명 |
|------|------|
| `--backup` | 기존 `.claude/` 백업 후 진행 |
| `--force` | 기존 파일 덮어쓰기 |
| `--template <type>` | 프로젝트 타입별 템플릿 (node, python, rust, go) |
| `--minimal` | 최소 구조만 생성 (knowledge 파일 생략) |
| `--with-hooks` | 로컬 hooks 디렉토리도 생성 |

## 프로젝트 타입별 템플릿

### Node.js (`--template node`)
- `package.json` 스크립트 자동 감지
- Jest/Vitest 테스트 설정 인식
- ESLint/Prettier 설정 참조

### Python (`--template python`)
- `pyproject.toml` / `setup.py` 감지
- pytest 설정 인식
- ruff/black 설정 참조

### Rust (`--template rust`)
- `Cargo.toml` 워크스페이스 감지
- clippy 설정 참조

### Go (`--template go`)
- `go.mod` 모듈 구조 감지
- golangci-lint 설정 참조

## 마이그레이션 후 확인사항

1. **CLAUDE.md 검토**: 프로젝트 설명 업데이트
2. **context.md 작성**: 현재 작업 컨텍스트 기록
3. **patterns.md 문서화**: 기존 코드 패턴 정리
4. **테스트**: 새 세션에서 컨텍스트 로드 확인

## 롤백

마이그레이션 취소:
```bash
# 백업이 있는 경우
mv .claude.backup .claude

# 전체 삭제
rm -rf .claude
```
