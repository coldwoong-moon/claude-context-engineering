#!/bin/bash
# Claude Context Engineering - 설치 스크립트
# 크로스플랫폼: macOS, Linux 지원

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       Claude Context Engineering - Installer              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_SRC="$PROJECT_ROOT/claude"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

echo -e "${YELLOW}[1/5] 환경 확인...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python 필요${NC}"
    exit 1
fi
echo -e "  ✓ Python: $($PYTHON_CMD --version)"

[ ! -d "$CLAUDE_HOME" ] && mkdir -p "$CLAUDE_HOME"
echo -e "  ✓ Claude Home: $CLAUDE_HOME"

[ ! -d "$CLAUDE_SRC" ] && { echo -e "${RED}Error: $CLAUDE_SRC 없음${NC}"; exit 1; }
echo -e "  ✓ Source: $CLAUDE_SRC"

echo -e "${YELLOW}[2/5] 백업...${NC}"
BACKUP_DIR="$CLAUDE_HOME/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
for item in commands hooks agents skills settings.json; do
    [ -e "$CLAUDE_HOME/$item" ] && cp -r "$CLAUDE_HOME/$item" "$BACKUP_DIR/" 2>/dev/null || true
done
echo -e "  ✓ $BACKUP_DIR"

echo -e "${YELLOW}[3/5] 디렉토리 생성...${NC}"
for dir in commands hooks agents skills knowledge; do
    mkdir -p "$CLAUDE_HOME/$dir"
done

echo -e "${YELLOW}[4/5] 파일 설치...${NC}"
[ -d "$CLAUDE_SRC/commands" ] && cp -r "$CLAUDE_SRC/commands"/* "$CLAUDE_HOME/commands/" 2>/dev/null || true
[ -d "$CLAUDE_SRC/hooks" ] && { cp -r "$CLAUDE_SRC/hooks"/* "$CLAUDE_HOME/hooks/" 2>/dev/null || true; chmod +x "$CLAUDE_HOME/hooks"/*.py 2>/dev/null || true; }
[ -d "$CLAUDE_SRC/agents" ] && cp -r "$CLAUDE_SRC/agents"/* "$CLAUDE_HOME/agents/" 2>/dev/null || true
[ -d "$CLAUDE_SRC/skills" ] && cp -r "$CLAUDE_SRC/skills"/* "$CLAUDE_HOME/skills/" 2>/dev/null || true
[ -f "$CLAUDE_SRC/settings.json" ] && cp "$CLAUDE_SRC/settings.json" "$CLAUDE_HOME/settings.json"
echo -e "  ✓ 완료"

echo -e "${YELLOW}[5/5] 검증...${NC}"
[ -f "$CLAUDE_HOME/commands/loop.md" ] && echo -e "  ✓ /loop" || echo -e "${RED}  ✗ /loop${NC}"
[ -f "$CLAUDE_HOME/commands/continuous.md" ] && echo -e "  ✓ /continuous" || echo -e "${RED}  ✗ /continuous${NC}"
[ -f "$CLAUDE_HOME/hooks/unified-loop.py" ] && echo -e "  ✓ unified-loop.py" || echo -e "${RED}  ✗ unified-loop.py${NC}"

echo -e "\n${GREEN}설치 완료!${NC}\n"
echo -e "명령어: /loop, /continuous, /research"
echo -e "완료: LOOP_COMPLETE | 취소: LOOP_CANCEL"
