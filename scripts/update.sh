#!/bin/bash
# Claude Context Engineering - 업데이트 스크립트

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Claude Context Engineering - Update${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Git pull
cd "$PROJECT_ROOT"
echo -e "${YELLOW}Pulling latest changes...${NC}"
git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "Git pull skipped"

# 설치 스크립트 재실행
echo -e "${YELLOW}Reinstalling...${NC}"
"$SCRIPT_DIR/install.sh"

echo -e "${GREEN}Update complete!${NC}"
