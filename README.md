# AI Tools Context-Engineering

> Cross-device synchronization for Claude Code, Gemini CLI, and Codex configurations

여러 기기에서 동일한 AI 도구 환경(hooks, agents, plugins, settings)을 사용할 수 있도록 GitHub을 통해 동기화하는 시스템입니다.

## 🚀 Quick Install (All Platforms)

**Windows, macOS, Linux** 모두 동일한 명령어로 설치:

```bash
# 1. Clone
git clone https://github.com/coldwoong-moon/claude-context-engineering.git
cd claude-context-engineering

# 2. Install (2가지 방법 중 선택)

# Option A: Python (Node.js 불필요)
python scripts/setup.py install

# Option B: Node.js
npm run setup

# 3. Verify
python scripts/setup.py doctor
# 또는
npm run doctor
```

### 기존 설치 업데이트

이미 설치된 환경에서 최신 버전으로 업데이트:

```bash
cd claude-context-engineering
git pull  # 또는 update 명령어가 자동으로 실행

# Python
python scripts/setup.py update

# 또는 Node.js
npm run update
```

> `update` 명령어는 settings.json을 유지하고 hooks와 commands만 업데이트합니다.

### 설치 확인

```
🔍 Running diagnostics...
──────────────────────────────────────────────────
✓ Python (python3)
✓ ~/.claude directory
✓ Hooks directory (17 hooks)
✓ Commands directory (4 commands)
✓ settings.json (Hooks configured)
✓ Claude Code CLI
──────────────────────────────────────────────────
✓ All checks passed!
```

### CLI 명령어

**Python 사용 (권장 - 추가 의존성 불필요)**

| 명령어 | 설명 |
|--------|------|
| `python scripts/setup.py install` | 전체 설치 (hooks + commands + config) |
| `python scripts/setup.py update` | 기존 설치 업데이트 (git pull + hooks + commands) |
| `python scripts/setup.py hooks` | hooks만 설치 |
| `python scripts/setup.py commands` | commands만 설치 |
| `python scripts/setup.py config` | settings.json만 설정 |
| `python scripts/setup.py project` | 현재 프로젝트 초기화 |
| `python scripts/setup.py doctor` | 설치 진단 |
| `python scripts/setup.py uninstall` | 설정 제거 |

**Node.js 사용**

| 명령어 | 설명 |
|--------|------|
| `npm run setup` | 전체 설치 (hooks + commands + config) |
| `npm run update` | 기존 설치 업데이트 (git pull + hooks + commands) |
| `npm run setup:hooks` | hooks만 설치 |
| `npm run setup:commands` | commands만 설치 |
| `npm run setup:config` | settings.json만 설정 |
| `npm run setup:project` | 현재 프로젝트를 Claude 프로젝트로 초기화 |
| `npm run doctor` | 설치 진단 및 문제 확인 |
| `npm run uninstall` | hooks 설정 제거 |

### 프로젝트 초기화

**방법 1: 설치 스크립트 사용**
```bash
# 프로젝트 디렉토리에서 실행
cd your-project
python ~/claude-context-engineering/scripts/setup.py project
# 또는
node ~/claude-context-engineering/scripts/setup.js project
```

**방법 2: Claude Code 내에서 slash command 사용 (권장)**
```bash
# Claude Code 세션에서
/migrate-context-engineering
```

생성되는 구조:
```
your-project/
└── .claude/
    ├── CLAUDE.md          # 프로젝트 엔트리포인트
    └── knowledge/
        ├── context.md     # 프로젝트 컨텍스트
        ├── decisions.md   # 아키텍처 결정
        ├── patterns.md    # 코드 패턴
        └── errors.md      # 알려진 오류
```

### Slash Commands

설치 시 자동으로 `~/.claude/commands/`에 설치되는 slash commands:

| Command | 설명 |
|---------|------|
| `/migrate-context-engineering` | 프로젝트를 Context Engineering 구조로 마이그레이션 |
| `/commit-push-pr` | 변경사항 커밋, 푸시, PR 생성 |
| `/code-simplifier` | 코드 단순화 및 리팩토링 |
| `/verify-app` | 앱 검증 및 테스트 실행 |

## Supported Tools

| Tool | Synced Items |
|------|-------------|
| **Claude Code** | hooks, agents, output-styles, settings.json (enabledPlugins, hooks) |
| **Gemini CLI** | settings.json, extensions, GEMINI.md |
| **Codex** | config.toml (model settings), prompts, skills |

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Device A                    GitHub                    Device B │
│                                                                 │
│  ~/.claude/                   ↕                     ~/.claude/  │
│  ~/.gemini/    ←────── context-engineering ──────→  ~/.gemini/  │
│  ~/.codex/               Repository                 ~/.codex/   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Cross-Platform**: Windows, macOS, Linux 모두 지원
- **One Command Install**: `npm run setup`으로 전체 설치
- **Multi-Tool Sync**: Claude Code, Gemini CLI, Codex 설정을 한 곳에서 관리
- **Automatic Sync**: Claude 세션 시작 시 자동으로 최신 설정 pull
- **Selective Sync**: 특정 도구만 동기화 가능 (`--claude`, `--gemini`, `--codex`)
- **Safe Merge**: settings.json은 특정 키만 병합 (전체 덮어쓰기 방지)
- **Lock Prevention**: 동시 실행 방지로 충돌 없는 동기화

## Manual Install (Alternative)

자동 설치가 작동하지 않는 경우:

```bash
# 1. Clone
git clone https://github.com/coldwoong-moon/claude-context-engineering.git ~/claude-context-engineering

# 2. Install
cd ~/claude-context-engineering
chmod +x scripts/*.sh
./scripts/sync.sh

# 3. Verify
./scripts/verify.sh
```

## Directory Structure

```
claude-context-engineering/
├── hooks/                    # Hook 스크립트 (17개) - 설치 시 ~/.claude/hooks/로 복사
│   ├── magic-keywords.py     # 매직 키워드 감지
│   ├── continuation-enforcer.py  # 작업 완료 강제
│   ├── context-window-monitor.py # 컨텍스트 모니터링
│   ├── session-recovery.py   # 세션 복구
│   └── ...
│
├── commands/                 # Slash Commands (4개) - 설치 시 ~/.claude/commands/로 복사
│   ├── migrate-context-engineering.md
│   ├── commit-push-pr.md
│   ├── code-simplifier.md
│   └── verify-app.md
│
├── scripts/                  # 설치 및 관리 스크립트
│   ├── setup.py              # Python 설치 스크립트
│   ├── setup.js              # Node.js 설치 스크립트
│   ├── sync.sh               # 동기화 실행
│   └── verify.sh             # 상태 확인
│
├── claude/                   # Claude Code 문서 및 설정
│   ├── CLAUDE.md             # 엔트리포인트
│   ├── CROSS-PLATFORM.md     # 크로스 플랫폼 가이드
│   └── ORCHESTRATOR-AGENTS.md # 에이전트 오케스트레이션
│
├── gemini/                   # Gemini CLI 설정
│   ├── settings.json         # UI/보안 설정
│   ├── extensions/           # MCP 확장
│   └── GEMINI.md             # 시스템 프롬프트
│
├── codex/                    # Codex 설정
│   ├── config.toml           # 모델 설정 (프로젝트 경로 제외)
│   ├── prompts/              # 커스텀 프롬프트
│   └── skills/               # 스킬 정의
│
├── package.json              # npm 패키지 설정
├── VERSION                   # 버전 정보
└── README.md
```

## Sync Commands

```bash
# 모든 도구 동기화 (GitHub → Local)
~/claude-context-engineering/scripts/sync.sh

# 특정 도구만 동기화
~/claude-context-engineering/scripts/sync.sh --claude
~/claude-context-engineering/scripts/sync.sh --gemini
~/claude-context-engineering/scripts/sync.sh --codex

# 조용한 동기화 (세션 시작용)
~/claude-context-engineering/scripts/sync.sh --quiet

# 로컬 변경사항 push
~/claude-context-engineering/scripts/sync.sh --push
```

## Automatic Sync (Claude)

Claude Code 세션 시작 시 자동 동기화:

```
Claude Code 시작
     ↓
session-start.py 실행
     ↓
sync.sh --quiet 호출
     ↓
GitHub에서 git pull
     ↓
Claude/Gemini/Codex 모두 동기화
     ↓
Ultrathink + Context 로드
```

## What Gets Synced

### Claude Code

| Source | Destination | Sync Method |
|--------|-------------|-------------|
| `claude/hooks/` | `~/.claude/hooks/` | 전체 복사 |
| `claude/agents/` | `~/.claude/agents/` | 전체 복사 |
| `claude/output-styles/` | `~/.claude/output-styles/` | 전체 복사 |
| `claude/settings.json` | `~/.claude/settings.json` | `enabledPlugins`, `hooks` 키만 병합 |

### Gemini CLI

| Source | Destination | Sync Method |
|--------|-------------|-------------|
| `gemini/settings.json` | `~/.gemini/settings.json` | 전체 복사 |
| `gemini/extensions/` | `~/.gemini/extensions/` | 전체 복사 |
| `gemini/GEMINI.md` | `~/.gemini/GEMINI.md` | 전체 복사 |

### Codex

| Source | Destination | Sync Method |
|--------|-------------|-------------|
| `codex/config.toml` | `~/.codex/config.toml` | `model`, `model_reasoning_effort`만 병합 |
| `codex/prompts/` | `~/.codex/prompts/` | 전체 복사 |
| `codex/skills/` | `~/.codex/skills/` | 전체 복사 |

## What is NOT Synced

| Tool | Excluded | Reason |
|------|----------|--------|
| **Claude** | `.credentials.json`, `history.jsonl`, `plugins/cache/` | 인증/개인정보 |
| **Gemini** | `oauth_creds.json`, `google_account_id` | 인증정보 |
| **Codex** | `auth.json`, `history.jsonl`, project trust levels | 인증/로컬경로 |

## New Device Setup

```bash
# 1. Clone
git clone https://github.com/coldwoong-moon/claude-context-engineering.git ~/claude-context-engineering

# 2. Sync
cd ~/claude-context-engineering
chmod +x scripts/*.sh
./scripts/sync.sh

# 3. Verify
./scripts/verify.sh

# 4. Done! Claude/Gemini/Codex 모두 동기화됨
```

## Customization

### Claude Hook 추가

```bash
# hooks/ 디렉토리에 새 hook 생성
vim ~/claude-context-engineering/claude/hooks/my-hook.py

# templates/hooks-config.json 업데이트
# Push
~/claude-context-engineering/scripts/sync.sh --push
```

### Gemini Extension 추가

```bash
# extensions/ 디렉토리에 추가
cp -r my-extension ~/claude-context-engineering/gemini/extensions/

# Push
~/claude-context-engineering/scripts/sync.sh --push
```

### Codex Prompt 추가

```bash
# prompts/ 디렉토리에 추가
vim ~/claude-context-engineering/codex/prompts/my-prompt.md

# Push
~/claude-context-engineering/scripts/sync.sh --push
```

## Troubleshooting

### Sync 실패 시

```bash
cd ~/claude-context-engineering
git status
git pull origin main
```

### jq 미설치 경고 (Claude settings 병합 불가)

```bash
# macOS
brew install jq

# Ubuntu
sudo apt-get install jq
```

### Hook 미작동 시

```bash
chmod +x ~/.claude/hooks/*.py
```

## Magic Keywords (oh-my-opencode Pattern)

Claude Code 세션에서 매직 키워드로 모드 자동 활성화:

| Keyword | Aliases | Description |
|---------|---------|-------------|
| `ultrawork` | `ulw`, `/ultra` | 전체 기능 최대 활성화 (TDD + TODO 필수) |
| `deepwork` | `dw`, `/deep` | 깊은 분석 모드 |
| `quickfix` | `qf`, `/quick` | 빠른 수정 모드 |
| `research` | `rs`, `/research` | 리서치 모드 |
| `security` | `sec`, `/security` | 보안 감사 모드 |
| `refactor` | `rf`, `/refactor` | 리팩토링 모드 |

### 암묵적 모드 (다국어 지원)

검색/분석 키워드 자동 감지 (한국어, 일본어, 중국어 포함):

```
"이 파일을 찾아줘" → SEARCH 모드 활성화
"코드를 분석해줘" → ANALYZE 모드 활성화
```

## Context Engineering Hooks

설치 시 자동 설정되는 18개의 hooks:

| Hook | Event | 기능 |
|------|-------|------|
| `magic-keywords.py` | UserPromptSubmit | 매직 키워드 감지 및 모드 활성화 |
| `continuation-enforcer.py` | SubagentStop, Stop | 미완료 작업 감지 및 연속 작업 강제 |
| `context-window-monitor.py` | PreCompact | 컨텍스트 사용량 모니터링 |
| `session-recovery.py` | SessionStart | 비정상 종료 복구 |
| `session-start.py` | SessionStart | 세션 초기화 및 동기화 |
| `pre-bash.py` | PreToolUse | Bash 실행 전 검증 |
| `post-bash.py` | PostToolUse | 오류 자동 기록 |
| `pre-edit.py` | PreToolUse | 파일 수정 전 검증 |
| `post-edit.py` | PostToolUse | 수정 추적 |

## Platform Support

| Platform | Python Command | Home Directory | Status |
|----------|---------------|----------------|--------|
| Windows | `python` | `%USERPROFILE%` | ✅ 지원 |
| macOS | `python` / `python3` | `~` | ✅ 지원 |
| Linux | `python` / `python3` | `~` | ✅ 지원 |

자세한 플랫폼별 설정은 [CROSS-PLATFORM.md](claude/CROSS-PLATFORM.md) 참조.

## Philosophy

이 시스템은 **Manus-style Context Engineering** 원칙을 따릅니다:

- **컨텍스트 오염 방지**: 복잡한 작업은 서브에이전트로 분리
- **날조 임계점 준수**: 8개 이상 항목은 반드시 중간 검증
- **오류는 자산**: 오류 메시지는 축적하여 학습 자원으로 활용
- **파일 = 무한 메모리**: 중요 결정/패턴은 영속화
- **TODO 필수**: 멀티스텝 작업은 반드시 TODO 관리 (oh-my-opencode)
- **검증 필수**: "증거 없음 = 완료 아님" (oh-my-opencode)

## Requirements

- **Node.js** 18 이상
- **Python** 3.9 이상
- **Claude Code CLI** 설치됨

## License

MIT License

---

> "Work, delegate, verify, ship. No AI slop." - oh-my-opencode
