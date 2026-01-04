# CROSS-PLATFORM.md - 크로스 플랫폼 설치 가이드

Windows, macOS, Linux에서 Claude Code Context Engineering 프레임워크를 설정하는 방법입니다.

## 빠른 설치 (권장)

모든 플랫폼에서 동일한 명령어로 설치:

```bash
# 저장소 클론
git clone https://github.com/coldwoong-moon/claude-context-engineering.git
cd claude-context-engineering

# 설치 실행 (2가지 방법)

# Option A: Python (권장 - 추가 의존성 불필요)
python scripts/setup.py install

# Option B: Node.js
npm run setup

# 설치 확인
python scripts/setup.py doctor
```

### CLI 명령어 (Python)

| 명령어 | 설명 |
|--------|------|
| `python scripts/setup.py install` | 전체 설치 (hooks + config) |
| `python scripts/setup.py hooks` | hooks만 설치 |
| `python scripts/setup.py config` | settings.json만 설정 |
| `python scripts/setup.py project` | 현재 디렉토리를 Claude 프로젝트로 초기화 |
| `python scripts/setup.py doctor` | 설치 진단 |
| `python scripts/setup.py uninstall` | 설정 제거 |

### CLI 명령어 (Node.js)

| 명령어 | 설명 |
|--------|------|
| `npm run setup` | 전체 설치 (hooks + config) |
| `npm run setup:hooks` | hooks만 설치 |
| `npm run setup:config` | settings.json만 설정 |
| `npm run setup:project` | 현재 디렉토리를 Claude 프로젝트로 초기화 |
| `npm run doctor` | 설치 진단 |
| `npm run uninstall` | 설정 제거 |

## 플랫폼별 요구사항

### 공통 요구사항
- Node.js 18 이상
- Python 3.9 이상
- Claude Code CLI 설치

### Windows
```powershell
# Python 설치 확인
python --version

# Claude Code 설치
npm install -g @anthropic/claude-code
```

### macOS / Linux
```bash
# Python 설치 확인
python3 --version

# Claude Code 설치
npm install -g @anthropic/claude-code
```

## 수동 설치 방법

자동 설치가 작동하지 않는 경우 수동으로 설치합니다.

### 1. hooks 디렉토리 복사

#### Windows (PowerShell)
```powershell
# hooks 디렉토리 생성
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\hooks"

# hooks 파일 복사 (저장소에서)
Copy-Item -Path ".\hooks\*" -Destination "$env:USERPROFILE\.claude\hooks\" -Recurse
```

#### macOS / Linux
```bash
# hooks 디렉토리 생성
mkdir -p ~/.claude/hooks

# hooks 파일 복사 (저장소에서)
cp -r ./hooks/* ~/.claude/hooks/
```

### 2. settings.json 설정

#### Windows
Windows 전용 템플릿 사용:
```powershell
# 템플릿 복사
Copy-Item -Path "$env:USERPROFILE\.claude\hooks\settings-windows.json.template" -Destination "$env:USERPROFILE\.claude\settings.json"
```

또는 수동으로 `%USERPROFILE%\.claude\settings.json`에 hooks 설정 추가:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python \"%USERPROFILE%\\.claude\\hooks\\session-recovery.py\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

#### macOS / Linux
```bash
# 기존 설정에 병합 또는 새로 생성
cp ./settings.json ~/.claude/settings.json
```

## 플랫폼별 차이점

| 항목 | Windows | macOS/Linux |
|------|---------|-------------|
| Python 명령어 | `python` | `python` 또는 `python3` |
| 홈 디렉토리 | `%USERPROFILE%` | `~` |
| 경로 구분자 | `\` | `/` |
| 환경변수 설정 | `set VAR=value &&` | `VAR=value` |

## 환경변수 설정

### Windows (PowerShell)
```powershell
# 시스템 환경변수 설정
[Environment]::SetEnvironmentVariable("CLAUDE_PROJECT_DIR", "C:\path\to\project", "User")
```

### Windows (CMD)
```cmd
set CLAUDE_PROJECT_DIR=C:\path\to\project
```

### macOS / Linux
```bash
export CLAUDE_PROJECT_DIR=/path/to/project
```

## 문제 해결

### Windows에서 python 명령어를 찾을 수 없음

1. Python이 PATH에 추가되어 있는지 확인:
```powershell
$env:Path -split ';' | Where-Object { $_ -like '*python*' }
```

2. Python 설치 시 "Add Python to PATH" 옵션 선택 필요

3. 또는 py 런처 사용:
```json
{
  "command": "py -3 \"%USERPROFILE%\\.claude\\hooks\\magic-keywords.py\""
}
```

### hooks 파일을 찾을 수 없음

경로가 올바른지 확인:
```powershell
# Windows
Test-Path "$env:USERPROFILE\.claude\hooks\magic-keywords.py"
```

```bash
# macOS/Linux
ls -la ~/.claude/hooks/magic-keywords.py
```

### 인코딩 오류 (Windows)

Python 파일 시작 부분에 인코딩 선언 확인:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

Windows 콘솔 인코딩 설정:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 환경변수가 전달되지 않음 (Windows)

Windows CMD 구문 사용:
```json
{
  "command": "set CLAUDE_HOOK_EVENT=Stop && python \"%USERPROFILE%\\.claude\\hooks\\hook.py\""
}
```

## 크로스 플랫폼 개발 가이드

hooks 개발 시 플랫폼 호환성 유지:

```python
from pathlib import Path
import platform

# 플랫폼 감지
IS_WINDOWS = platform.system() == "Windows"

# 홈 디렉토리 (크로스 플랫폼)
home = Path.home()

# 경로 조합 (pathlib 사용)
hooks_dir = home / ".claude" / "hooks"

# 파일 읽기 (인코딩 명시)
content = filepath.read_text(encoding="utf-8")
```

## 테스트

설치 확인:
```bash
# hook 실행 테스트
python ~/.claude/hooks/run-hook.py magic-keywords
```

Windows:
```powershell
python "%USERPROFILE%\.claude\hooks\run-hook.py" magic-keywords
```
