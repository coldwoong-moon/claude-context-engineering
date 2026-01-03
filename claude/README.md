# Claude Code Context Engineering

> 체계적인 Claude Code 환경 구성을 위한 Context Engineering 시스템
>
> **v1.1.0** - Oh-My-OpenCode + Boris Cheny 패턴 통합

## 적용된 패턴

| 출처 | 패턴 | 구현 |
|------|------|------|
| **Oh-My-OpenCode** | Ralph Loop | `ralph-loop.py` |
| **Oh-My-OpenCode** | Librarian (증거 기반) | `librarian.md` |
| **Oh-My-OpenCode** | Context Isolation | `task-worker.md` |
| **Boris Cheny** | Verification Loop | `verification-loop.py` |
| **Boris Cheny** | Slash Commands | `commands/` |
| **Boris Cheny** | CLAUDE.md Compounding | `CLAUDE.md.template` |

## 구조

```
claude/
├── hooks/                    # 이벤트 기반 자동화 (13개)
│   ├── utils.py              # 공통 유틸리티
│   ├── session-start.py      # 세션 시작: 동기화 + 컨텍스트 로드
│   ├── pre-bash.py           # Bash 실행 전: 위험 명령 차단
│   ├── post-bash.py          # Bash 실행 후: 오류 자동 기록
│   ├── pre-edit.py           # 파일 수정 전: 중요 파일 보호
│   ├── post-edit.py          # 파일 수정 후: 변경 추적
│   ├── pre-mcp.py            # MCP 도구 전: 민감 작업 경고
│   ├── ralph-loop.py         # ✨ 완료까지 작업 지속 강제
│   ├── verification-loop.py  # ✨ 서브에이전트 완료 시 검증
│   └── ...
│
├── agents/                   # 전문화된 서브에이전트 (8개)
│   ├── task-worker.md        # 단일 작업 (Context Isolation)
│   ├── researcher.md         # 심층 연구/조사
│   ├── documenter.md         # 기술 문서 작성
│   ├── test-writer.md        # 테스트 개발
│   └── librarian.md          # ✨ 증거 기반 리서치 (Zero Hallucination)
│
├── commands/                 # ✨ Slash Commands (Boris Cheny 패턴)
│   ├── commit-push-pr.md     # Git 워크플로우 자동화
│   ├── verify-app.md         # 앱 검증 워크플로우
│   └── code-simplifier.md    # 코드 단순화
│
├── output-styles/            # 출력 스타일 프리셋 (5개)
│   ├── concise.md            # 간결 모드
│   ├── researcher.md         # 연구자 모드
│   ├── teacher.md            # 교육자 모드
│   └── debugger.md           # 디버거 모드
│
└── templates/                # 설정 템플릿
    ├── settings-core.json          # 필수 플러그인 (14개)
    ├── settings-optional.json      # 선택 플러그인 (26개)
    ├── settings-recommended.json   # 권장 구성 (40개)
    ├── hooks-config.json           # Hook 설정 템플릿
    └── CLAUDE.md.template          # ✨ Compounding 템플릿
```

## 핵심 개념

### 1. Ralph Loop - 완료까지 지속

Oh-My-OpenCode의 핵심 패턴: 명시적 완료 태그까지 작업 지속

```
[작업 시작]
    ↓
[작업 수행]
    ↓
[완료 태그 없음?] → "다음 작업 있음" 알림 → [계속]
    ↓
[TASK_COMPLETE] → 종료
```

### 2. Librarian Agent - Zero Hallucination

모든 주장에 증거 필수:
- GitHub Permalink (코드 참조)
- 공식 문서 링크
- Issue/PR 번호
- 불확실한 내용은 `[UNVERIFIED]` 표시

### 3. Verification Loop - 품질 2~3배 향상

Boris Cheny의 검증 루프:
- 서브에이전트 완료 시 자동 검증 체크리스트
- 작업 유형별 맞춤 검증 (bugfix, feature, refactor)
- Fabrication Risk 감지

### 4. Context Isolation - Context Rot 방지

각 서브에이전트의 컨텍스트 격리:
- 메인 대화와 독립된 컨텍스트
- 작업 범위 엄격 제한
- 요약된 결과만 상위 전달

### 5. CLAUDE.md Compounding

팀 전체가 Git에 체크인하는 공유 파일:
- Claude 실수 시마다 추가
- 주 단위 팀원 기여
- 코드 리뷰 시 @claude 태그로 업데이트

## Slash Commands

Boris Cheny 패턴: `.claude/commands/`에 반복 워크플로우 저장

```bash
/commit-push-pr    # 커밋 → 푸시 → PR
/verify-app        # 린터 + 타입체크 + 테스트 + 빌드
/code-simplifier   # 코드 단순화
```

## Hooks 트리거

| Hook | 트리거 | 역할 |
|------|--------|------|
| `session-start.py` | SessionStart | 동기화 + 컨텍스트 로드 |
| `pre-bash.py` | PreToolUse:Bash | 위험 명령 차단 |
| `post-bash.py` | PostToolUse:Bash | 오류 자동 기록 |
| `pre-edit.py` | PreToolUse:Edit\|Write | 중요 파일 보호 |
| `pre-mcp.py` | PreToolUse:mcp__* | MCP 도구 검증 |
| `ralph-loop.py` | Stop | 완료 확인 + 지속 유도 |
| `verification-loop.py` | SubagentStop | 작업 검증 체크리스트 |

## 7대 원칙 (업데이트)

1. **컨텍스트 격리**: 복잡한 작업은 서브에이전트로 분리 (Context Rot 방지)
2. **날조 임계점 (8개)**: 8개 이상 항목 시 중간 검증 필수
3. **오류는 자산**: 오류 메시지는 자동 축적
4. **파일 = 무한 메모리**: 중요 결정/패턴 영속화
5. **Ralph Loop**: 명시적 완료 태그까지 작업 지속
6. **증거 기반**: 모든 주장에 GitHub permalink 또는 문서 링크
7. **검증 루프**: 서브에이전트 완료 시 결정론적 검증

## 참고 자료

- [Anthropic Best Practices](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Manus Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Oh-My-OpenCode](https://github.com/YeonGyu-Kim/oh-my-opencode) - Ralph Loop, Librarian
- [Boris Cheny's 7 Techniques](https://www.linkedin.com/in/jyoung105) - Verification Loop, Slash Commands
