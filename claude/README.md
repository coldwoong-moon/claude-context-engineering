# Claude Code Context Engineering

> 체계적인 Claude Code 환경 구성을 위한 Context Engineering 시스템

## 구조

```
claude/
├── hooks/               # 이벤트 기반 자동화
│   ├── utils.py         # 공통 유틸리티
│   ├── session-start.py # 세션 시작: 동기화 + 컨텍스트 로드
│   ├── pre-bash.py      # Bash 실행 전: 위험 명령 차단
│   ├── post-bash.py     # Bash 실행 후: 오류 자동 기록
│   ├── pre-edit.py      # 파일 수정 전: 중요 파일 보호
│   ├── post-edit.py     # 파일 수정 후: 변경 추적
│   ├── pre-mcp.py       # MCP 도구 전: 민감 작업 경고
│   └── ...
│
├── agents/              # 전문화된 서브에이전트
│   ├── task-worker.md   # 단일 작업 처리
│   ├── researcher.md    # 심층 연구/조사
│   ├── documenter.md    # 기술 문서 작성
│   └── test-writer.md   # 테스트 개발
│
├── output-styles/       # 출력 스타일 프리셋
│   ├── concise.md       # 간결 모드
│   ├── researcher.md    # 연구자 모드
│   ├── teacher.md       # 교육자 모드
│   └── debugger.md      # 디버거 모드
│
└── templates/           # 설정 템플릿
    ├── settings-core.json       # 필수 플러그인 (15개)
    ├── settings-optional.json   # 선택 플러그인 (25개)
    ├── settings-recommended.json # 권장 구성 (40개)
    └── hooks-config.json        # Hook 설정 템플릿
```

## 핵심 개념

### 1. Hooks - 이벤트 기반 자동화

| Hook | 트리거 | 역할 |
|------|--------|------|
| `session-start.py` | SessionStart | 동기화 + 컨텍스트 로드 |
| `pre-bash.py` | PreToolUse:Bash | 위험 명령 차단 |
| `post-bash.py` | PostToolUse:Bash | 오류 자동 기록 |
| `pre-edit.py` | PreToolUse:Edit\|Write | 중요 파일 보호 |
| `pre-mcp.py` | PreToolUse:mcp__* | MCP 도구 검증 |

### 2. Agents - 전문화된 서브에이전트

컨텍스트 오염 방지를 위해 복잡한 작업을 분리:

```
Main Agent
    ↓ Task("심층 조사 필요")
    └── researcher agent
            ↓
        결과 반환 (요약)
```

### 3. Output Styles - 상황별 출력 조정

```bash
# 간결한 결과만 필요할 때
/concise

# 학습 목적일 때
/teacher
```

### 4. Settings Layering - 플러그인 계층화

```
core.json (15개)     ← 항상 활성화
    ↓
optional.json (25개) ← 필요시 추가
    ↓
recommended.json (40개) ← 권장 조합
```

## 사용법

### 1. 전체 동기화

```bash
~/claude-context-engineering/scripts/sync.sh
```

### 2. 플러그인 설정 적용

```bash
# 권장 설정 사용
jq -s '.[0] * .[1]' \
  ~/.claude/settings.json \
  ~/claude-context-engineering/claude/templates/settings-recommended.json \
  > ~/.claude/settings.json.tmp && \
  mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

### 3. 커스텀 Hook 추가

1. `hooks/` 디렉토리에 Python 스크립트 생성
2. `templates/hooks-config.json` 업데이트
3. `sync.sh --push`로 동기화

## 5대 원칙

1. **컨텍스트 오염 방지**: 복잡한 작업은 서브에이전트로 분리
2. **날조 임계점 (8개)**: 8개 이상 항목 시 중간 검증 필수
3. **오류는 자산**: 오류 메시지는 자동 축적
4. **파일 = 무한 메모리**: 중요 결정/패턴 영속화
5. **todo.md 되새김**: 세션 시작 시 작업 연속성 유지

## 참고 자료

- [Anthropic Best Practices](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Manus Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
