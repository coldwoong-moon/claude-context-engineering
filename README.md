# AI Tools Context-Engineering

> Cross-device synchronization for Claude Code, Gemini CLI, and Codex configurations

여러 기기에서 동일한 AI 도구 환경(hooks, agents, plugins, settings)을 사용할 수 있도록 GitHub을 통해 동기화하는 시스템입니다.

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

- **Multi-Tool Sync**: Claude Code, Gemini CLI, Codex 설정을 한 곳에서 관리
- **Automatic Sync**: Claude 세션 시작 시 자동으로 최신 설정 pull
- **Selective Sync**: 특정 도구만 동기화 가능 (`--claude`, `--gemini`, `--codex`)
- **Safe Merge**: settings.json은 특정 키만 병합 (전체 덮어쓰기 방지)
- **Lock Prevention**: 동시 실행 방지로 충돌 없는 동기화

## Quick Start

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
├── claude/                   # Claude Code 설정
│   ├── hooks/                # Hook 스크립트 (9개)
│   │   ├── session-start.py  # 세션 시작: Sync + Ultrathink
│   │   ├── pre-bash.py       # Bash 실행 전 검증
│   │   ├── post-bash.py      # 오류 자동 기록
│   │   ├── pre-edit.py       # 파일 수정 전 검증
│   │   ├── post-edit.py      # 수정 추적
│   │   └── ...
│   ├── agents/               # 커스텀 에이전트 (4개)
│   ├── output-styles/        # 출력 스타일
│   ├── settings.json         # 플러그인 & Hook 설정
│   └── templates/            # 설정 템플릿
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
├── scripts/
│   ├── sync.sh               # 동기화 실행
│   └── verify.sh             # 상태 확인
│
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

## Philosophy

이 시스템은 **Manus-style Context Engineering** 원칙을 따릅니다:

- **컨텍스트 오염 방지**: 복잡한 작업은 서브에이전트로 분리
- **날조 임계점 준수**: 8개 이상 항목은 반드시 중간 검증
- **오류는 자산**: 오류 메시지는 축적하여 학습 자원으로 활용
- **파일 = 무한 메모리**: 중요 결정/패턴은 영속화

## License

MIT License

---

> "Take a deep breath. We're not here to write code. We're here to make a dent in the universe."
