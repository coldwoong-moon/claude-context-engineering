# Context Engineering Framework

> 모든 작업에 원자화와 진화 피드백이 자동 적용됩니다.

## 핵심 원칙

```yaml
증거_우선: "모든 주장에 파일:라인 참조 필수"
원자_작업: "≤3 파일, ≤30분, 단일 책임, 독립 테스트 가능"
자동_진화: "작업 결과 → 메트릭 수집 → 패턴 학습 → 개선"
적재적소: "작업 특성에 따라 Claude/Gemini/Codex 자동 선택"
```

---

## 기본 워크플로우 (모든 작업에 자동 적용)

### 1. 요청 분석
```
사용자 요청 수신
    ↓
명시적 + 암묵적 요구사항 추출
    ↓
작업 범위 및 영향 평가
```

### 2. 작업 원자화 (자동)
```
큰 작업 감지 시 자동 분해:
- 각 작업 ≤3 파일 영향
- 각 작업 ≤30분 내 완료
- 의존성 그래프 생성
- TodoWrite로 추적
```

### 3. 멀티AI 자동 라우팅 (자동)
```yaml
# 상황에 따라 자동으로 적절한 AI 호출

대규모_분석: # 자동으로 Gemini 호출
  조건: 분석 대상 >50 파일 OR 컨텍스트 >100K 토큰
  실행: gemini -p "<분석 프롬프트>" -f <파일들>
  예시:
    - 전체 코드베이스 패턴 분석
    - 시각적 UI 일관성 검토
    - 대규모 리팩토링 영향 분석

빠른_생성: # 자동으로 Codex 호출
  조건: 보일러플레이트 OR 반복적 코드 생성
  실행: codex "<생성 프롬프트>"
  예시:
    - 테스트 파일 대량 생성
    - API 스캐폴딩
    - CRUD 엔드포인트 생성

복잡_추론: # Claude 기본 처리
  조건: 아키텍처 결정, 디버깅, 리뷰, 보안 분석
  예시:
    - 코드 리뷰 및 개선
    - 버그 원인 분석
    - 설계 결정
```

### 4. 실행 및 검증
```
원자 작업 실행
    ↓
품질 게이트 (lint, test, security)
    ↓
결과 검증
    ↓
다음 작업 또는 완료
```

### 5. 진화 피드백 (자동)
```
세션 종료 시:
- 예측 vs 실제 비교
- 패턴 학습 및 저장
- 개선 권장사항 생성
```

---

## Moon Commands (통합 명령어)

| 명령어 | 설명 | 주요 기능 |
|--------|------|----------|
| `/moon-loop <goal>` | 목표 달성까지 자율 연속 실행 | Ralph + Continuous + TDD 통합 |
| `/moon-research <topic>` | 심층 연구 (학술 + 웹) | Multi-AI 오케스트레이션 |
| `/moon-review <target>` | 비판적 코드/아키텍처 리뷰 | Feedback + Feedforward |
| `/moon-cancel` | 진행 중인 루프 취소 | 상태 저장 후 안전 종료 |

### Moon-Loop 모드
```bash
/moon-loop "목표" --mode continuous|ralph|tdd --max 10 --verify "npm test"
```

### Moon-Research 옵션
```bash
/moon-research "주제" --academic --web --cite apa|bibtex --depth quick|standard|deep
```

### Moon-Review 옵션
```bash
/moon-review <target> --scope code|arch|security|perf|all --depth quick|standard|deep
```

---

## 한국어 키워드 (대화 중 사용)

| 키워드 | 동작 |
|--------|------|
| `연구: <주제>` | `/moon-research` 실행 |
| `리뷰: <대상>` | `/moon-review` 실행 |
| `루프: <목표>` | `/moon-loop` 실행 |
| `취소` | `/moon-cancel` 실행 |

---

## AI 라우팅 상세

### Gemini CLI 자동 호출 조건

```yaml
triggers:
  - 분석 대상 파일 >50개
  - 컨텍스트 크기 >100K 토큰
  - UI/시각적 분석 요청
  - 전체 코드베이스 패턴 검색

usage:
  pattern_analysis: |
    gemini -p "코드베이스에서 [패턴] 분석" -f "src/**/*.ts"

  ui_review: |
    gemini -p "UI 일관성 검토" -f "src/components/**/*" screenshot.png

  large_refactor: |
    gemini -p "리팩토링 영향 분석" -f "src/**/*"
```

### Codex CLI 자동 호출 조건

```yaml
triggers:
  - 테스트 파일 대량 생성
  - CRUD/API 보일러플레이트
  - 프레임워크 스캐폴딩
  - 반복적 코드 패턴

usage:
  test_generation: |
    codex "UserService에 대한 단위 테스트 생성"

  api_scaffold: |
    codex "Express REST API 엔드포인트 생성: /api/users CRUD"

  component_batch: |
    codex "React 컴포넌트 생성: Button, Card, Modal"
```

### Claude 기본 처리

```yaml
specialization:
  - 복잡한 추론 및 분석
  - 코드 리뷰 및 품질 평가
  - 아키텍처 설계 결정
  - 보안 취약점 분석
  - 디버깅 및 문제 해결
  - 문서화 및 설명
```

---

## 품질 게이트 (모든 작업 후 자동)

```yaml
검증_항목:
  - lint/타입 체크 통과
  - 테스트 통과 (기존 실패는 문서화)
  - 보안 취약점 없음
  - 변경사항이 요구사항과 일치
```

---

## 파일 구조

```
.claude/
├── HANDOFF.md          # 연속 작업 상태 (루프 모드)
├── specs/              # 스펙 문서 (복잡한 기능)
├── knowledge/
│   ├── evolution/      # 진화 피드백 메트릭
│   └── research/       # 연구 결과
└── todo.md             # 작업 추적
```

---

## 워크플로우 예시

### 일반 기능 구현 요청
```
사용자: "사용자 인증 기능 추가해줘"

Claude 자동 처리:
1. 요구사항 분석 (명시적 + 암묵적)
2. 작업 원자화 (4개 작업으로 분해)
3. TodoWrite로 추적 시작
4. TASK-001 실행 → 검증 → 완료
5. TASK-002 실행 → 검증 → 완료
   ...
6. 진화 피드백 수집
```

### 대규모 분석 요청
```
사용자: "전체 코드베이스에서 보안 취약점 찾아줘"

Claude 자동 처리:
1. 파일 수 확인 → 150개 감지
2. Gemini CLI 자동 호출:
   gemini -p "보안 취약점 분석" -f "src/**/*"
3. Gemini 결과 수신
4. Claude가 결과 정리 및 우선순위화
5. 긴급 이슈는 TodoWrite로 추적
```

### 반복 작업 요청
```
사용자: "모든 서비스에 단위 테스트 추가해줘"

Claude 자동 처리:
1. 서비스 파일 목록 확인 → 20개
2. 패턴 분석 후 Codex CLI 호출:
   codex "서비스 단위 테스트 생성: UserService"
3. 생성된 테스트 검토 및 보완 (Claude)
4. 다음 서비스로 반복
5. 전체 완료 후 진화 피드백
```

---

## Claude Code 2.1+ 신기능 적용

> Claude Code 2.1.0+ 버전의 새로운 기능을 Context Engineering에 통합

### Skill Hot-Reload (자동 스킬 감지)
```yaml
# ~/.claude/skills/ 또는 .claude/skills/ 의 스킬 즉시 사용 가능
# 재시작 불필요

skill_directories:
  global: "~/.claude/skills/"
  project: ".claude/skills/"

hot_reload: true  # 파일 변경 시 자동 반영
```

### Forked Sub-Agent Context
```yaml
# 스킬 frontmatter에서 context: fork 사용
# 서브에이전트가 독립적인 컨텍스트에서 실행

---
name: my-skill
context: fork  # 메인 대화와 분리된 컨텍스트
agent: general-purpose
---
```

### Agent Hooks in Frontmatter
```yaml
# 스킬/커맨드 자체에 훅 정의 가능

---
name: my-command
hooks:
  PreToolUse:
    - matcher: "Bash"
      command: "python3 ~/.claude/hooks/safety-check.py"
  PostToolUse:
    - matcher: "Edit|Write"
      command: "python3 ~/.claude/hooks/progress-update.py"
  Stop:
    - command: "python3 ~/.claude/hooks/completion-check.py"
---
```

### Wildcard Tool Permissions (2.1 문법)
```yaml
# 새로운 와일드카드 패턴 지원

permissions:
  allow:
    - "Bash(npm *)"         # npm으로 시작하는 모든 명령
    - "Bash(* install)"     # install로 끝나는 모든 명령
    - "Bash(* --help)"      # --help로 끝나는 모든 명령
    - "mcp__*"              # 모든 MCP 도구
```

### LSP (Language Server Protocol) 도구
```yaml
# 코드 인텔리전스 기능
lsp_features:
  - go-to-definition
  - find-references
  - hover-documentation
  - symbol-search

# 지원 언어: TypeScript, Python, Go, Rust 등
```

### Real-Time Steering
```yaml
# Claude 작업 중 실시간 메시지 전송 가능
# 방향 수정, 추가 지시 등

usage: "Claude가 작업 중일 때 입력하면 즉시 반영"
```

### Background Tasks (Ctrl+B)
```yaml
# 모든 포그라운드 작업을 백그라운드로 전환
# 완료 시 알림

shortcut: "Ctrl+B"
notification: true
```

### MCP list_changed 알림
```yaml
# MCP 서버의 도구/리소스 변경 시 자동 업데이트
# 재연결 불필요

dynamic_updates: true
```

---

## 참조 문서

@SPEC-ATOMIZATION.md
@MULTI-AI-ORCHESTRATION.md
@CONTINUOUS-CLAUDE.md
@RESEARCH-MODE.md
