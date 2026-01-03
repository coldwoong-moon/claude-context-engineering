# Claude Context-Engineering

> Cross-device synchronization for Claude Code configurations

여러 기기에서 동일한 Claude Code 환경(hooks, agents, output-styles)을 사용할 수 있도록 GitHub을 통해 동기화하는 시스템입니다.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Device A                    GitHub                    Device B │
│                                                                 │
│  ~/.claude/                   ↕                     ~/.claude/  │
│  ├── hooks/     ←────── claude-context-engineering ──────→      │
│  ├── agents/              Repository                  hooks/    │
│  └── output-styles/                                   agents/   │
│                                                       output-   │
│                                                       styles/   │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Automatic Sync**: 세션 시작 시 자동으로 GitHub에서 최신 설정을 pull
- **Safe Backup**: 설치/동기화 전 기존 파일 자동 백업
- **Selective Sync**: 프로젝트별 설정(`.claude/`)은 제외, User-level 설정만 동기화
- **Lock Prevention**: 동시 실행 방지로 충돌 없는 동기화

## Installation

### Prerequisites

- macOS 또는 Linux
- Git 설치됨
- GitHub CLI (`gh`) 인증됨

### Quick Start

```bash
# 1. Repository clone
git clone https://github.com/coldwoong-moon/claude-context-engineering.git ~/claude-context-engineering

# 2. 설치 스크립트 실행
cd ~/claude-context-engineering
chmod +x scripts/*.sh
./scripts/install.sh
```

### What Gets Installed

| Source | Destination | Description |
|--------|-------------|-------------|
| `hooks/` | `~/.claude/hooks/` | Hook 스크립트 (9개) |
| `agents/` | `~/.claude/agents/` | 커스텀 에이전트 (4개) |
| `output-styles/` | `~/.claude/output-styles/` | 출력 스타일 (1개) |
| `templates/hooks-config.json` | `~/.claude/settings.json` (병합) | Hook 설정 |

## Directory Structure

```
claude-context-engineering/
├── hooks/                    # User-level hooks
│   ├── session-start.py      # 세션 시작: Ultrathink + Context 로드
│   ├── user-prompt-submit.py # 프롬프트 제출 시 처리
│   ├── pre-bash.py           # Bash 실행 전 검증
│   ├── post-bash.py          # Bash 실행 후 오류 기록
│   ├── pre-edit.py           # 파일 수정 전 검증
│   ├── post-edit.py          # 파일 수정 후 추적
│   ├── pre-compact.py        # 컨텍스트 압축 전 처리
│   ├── subagent-stop.py      # 서브에이전트 종료 시 처리
│   └── stop.py               # 세션 종료 시 리마인드
│
├── agents/                   # User-level agents
│   ├── task-worker.md        # 단일 작업 처리 에이전트
│   ├── code-reviewer.md      # 코드 리뷰 에이전트
│   ├── debugger.md           # 디버깅 전문 에이전트
│   └── mobile-developer.md   # 모바일 개발 에이전트
│
├── output-styles/            # Output styles
│   └── flutter-mobile-dev.md # Flutter 개발 스타일
│
├── templates/                # Configuration templates
│   └── hooks-config.json     # settings.json hooks 섹션
│
├── scripts/                  # Management scripts
│   ├── install.sh            # 최초 설치
│   └── sync.sh               # 동기화 실행
│
└── README.md                 # This file
```

## Synchronization

### Automatic (Recommended)

세션 시작 시 `session-start.py`가 자동으로 `sync.sh --quiet`를 호출합니다.

```
Claude Code 시작
     ↓
session-start.py 실행
     ↓
sync.sh --quiet 호출
     ↓
GitHub에서 git pull
     ↓
hooks/agents/output-styles 동기화
     ↓
Ultrathink + Context 로드
```

### Manual

```bash
# 수동 동기화 (GitHub → Local)
~/claude-context-engineering/scripts/sync.sh

# 로컬 변경사항 push (Local → GitHub)
~/claude-context-engineering/scripts/sync.sh --push

# 조용한 동기화 (로그 최소화)
~/claude-context-engineering/scripts/sync.sh --quiet
```

## Customization

### Adding a New Hook

1. `hooks/` 디렉토리에 Python 스크립트 생성
2. `templates/hooks-config.json`에 hook 설정 추가
3. 커밋 & 푸시

```bash
cd ~/claude-context-engineering
git add hooks/my-new-hook.py templates/hooks-config.json
git commit -m "feat: Add my-new-hook"
git push origin main
```

### Adding a New Agent

1. `agents/` 디렉토리에 Markdown 파일 생성
2. 커밋 & 푸시

```markdown
---
name: my-agent
description: 에이전트 설명
model: sonnet
---

에이전트 프롬프트 내용...
```

## New Device Setup

다른 기기에서 동일한 환경을 구성하려면:

```bash
# 1. Clone
git clone https://github.com/coldwoong-moon/claude-context-engineering.git ~/claude-context-engineering

# 2. Install
cd ~/claude-context-engineering
chmod +x scripts/*.sh
./scripts/install.sh

# 3. Done! 다음 Claude Code 세션부터 자동 동기화
```

## Hook Details

### session-start.py

세션 시작 시 실행되는 핵심 hook:

1. **Context-Engineering Sync**: GitHub에서 최신 설정 pull
2. **Ultrathink Philosophy**: Craftsman Mindset 배너 표시
3. **Environment Info**: 날짜, Git 브랜치, Docker 상태
4. **Project Context**: todo.md, knowledge 파일 로드

### pre-bash.py

위험한 명령어 차단:
- `rm -rf /`, `rm -rf ~`
- `mkfs`, `fdisk`
- `:(){ :|:& };:`

### post-bash.py

오류 발생 시 자동 기록:
- `.claude/knowledge/errors.md`에 오류 패턴 축적

### pre-edit.py

중요 파일 수정 경고:
- `CLAUDE.md`, `.env`, `settings.json` 등

## Troubleshooting

### Sync 실패 시

```bash
# 수동으로 상태 확인
cd ~/claude-context-engineering
git status
git pull origin main
```

### Hook 미작동 시

```bash
# 실행 권한 확인
ls -la ~/.claude/hooks/

# 권한 부여
chmod +x ~/.claude/hooks/*.py
```

### jq 미설치 경고

```bash
# macOS
brew install jq

# Ubuntu
sudo apt-get install jq
```

## What is NOT Synced

- `.credentials.json` - API 키, 인증 정보
- `history.jsonl` - 대화 기록
- `settings.json` (전체) - 로컬별 플러그인 설정
- `plugins/cache/` - 플러그인 캐시
- Project-level `.claude/` - 프로젝트별 설정

## Contributing

1. 이 저장소를 Fork
2. 변경사항 커밋
3. Pull Request 생성

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
