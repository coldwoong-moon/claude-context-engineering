#!/bin/bash
# Claude Context Engineering - 제거 스크립트

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Claude Context Engineering - Uninstall${NC}"

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

echo -e "제거 대상: $CLAUDE_HOME"
echo ""

# 백업 확인
if [ -d "$CLAUDE_HOME/backups" ]; then
    LATEST_BACKUP=$(ls -td "$CLAUDE_HOME/backups"/*/ 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo -e "${YELLOW}최근 백업: $LATEST_BACKUP${NC}"
        read -p "복원하시겠습니까? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp -r "$LATEST_BACKUP"/* "$CLAUDE_HOME/" 2>/dev/null || true
            echo -e "${GREEN}복원 완료${NC}"
            exit 0
        fi
    fi
fi

# 제거 확인
read -p "Context Engineering 파일을 제거하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소됨"
    exit 0
fi

# 제거
rm -rf "$CLAUDE_HOME/commands" 2>/dev/null || true
rm -rf "$CLAUDE_HOME/hooks" 2>/dev/null || true
rm -rf "$CLAUDE_HOME/agents" 2>/dev/null || true
rm -rf "$CLAUDE_HOME/skills" 2>/dev/null || true

echo -e "${GREEN}제거 완료${NC}"
echo "백업은 유지됨: $CLAUDE_HOME/backups/"
