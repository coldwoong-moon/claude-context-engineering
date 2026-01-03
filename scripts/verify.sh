#!/bin/bash
# =============================================================================
# Claude Context-Engineering Verification Script
# =============================================================================
# 동기화 상태 및 설치 상태를 확인합니다.
#
# 사용법:
#   ./scripts/verify.sh
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Claude Context-Engineering Verification                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. Repository 상태
echo -e "${YELLOW}[1/5]${NC} Repository Status"
if [[ -d "$REPO_DIR/.git" ]]; then
    VERSION=$(cat "$REPO_DIR/VERSION" 2>/dev/null || echo "unknown")
    COMMIT=$(git -C "$REPO_DIR" log -1 --format="%h %s" 2>/dev/null || echo "unknown")
    echo -e "  ${GREEN}✓${NC} Repository: $REPO_DIR"
    echo -e "  ${GREEN}✓${NC} Version: $VERSION"
    echo -e "  ${GREEN}✓${NC} Latest commit: $COMMIT"
else
    echo -e "  ${RED}✗${NC} Repository not found at $REPO_DIR"
fi

# 2. Hooks 동기화 확인
echo -e "\n${YELLOW}[2/5]${NC} Hooks Synchronization"
HOOKS_OK=true
for hook in session-start.py pre-bash.py post-bash.py pre-edit.py post-edit.py stop.py; do
    REPO_FILE="$REPO_DIR/hooks/$hook"
    LOCAL_FILE="$CLAUDE_DIR/hooks/$hook"

    if [[ -f "$REPO_FILE" ]] && [[ -f "$LOCAL_FILE" ]]; then
        if diff -q "$REPO_FILE" "$LOCAL_FILE" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $hook - synced"
        else
            echo -e "  ${YELLOW}!${NC} $hook - differs (local changes?)"
            HOOKS_OK=false
        fi
    elif [[ -f "$REPO_FILE" ]]; then
        echo -e "  ${RED}✗${NC} $hook - not installed"
        HOOKS_OK=false
    fi
done

# 3. Agents 동기화 확인
echo -e "\n${YELLOW}[3/5]${NC} Agents Synchronization"
AGENTS_COUNT=$(ls -1 "$REPO_DIR/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
INSTALLED_COUNT=$(ls -1 "$CLAUDE_DIR/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo -e "  Repository: $AGENTS_COUNT agents"
echo -e "  Installed:  $INSTALLED_COUNT agents"

# 4. Sync 로그 확인
echo -e "\n${YELLOW}[4/5]${NC} Recent Sync Activity"
LOG_FILE="$CLAUDE_DIR/logs/sync.log"
if [[ -f "$LOG_FILE" ]]; then
    LAST_SYNC=$(tail -1 "$LOG_FILE")
    SYNC_COUNT=$(wc -l < "$LOG_FILE" | tr -d ' ')
    echo -e "  ${GREEN}✓${NC} Log file exists ($SYNC_COUNT entries)"
    echo -e "  ${GREEN}✓${NC} Last: $LAST_SYNC"
else
    echo -e "  ${YELLOW}!${NC} No sync log found (first run?)"
fi

# 5. settings.json hooks 설정
echo -e "\n${YELLOW}[5/5]${NC} Hook Configuration"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [[ -f "$SETTINGS_FILE" ]]; then
    if grep -q "session-start.py" "$SETTINGS_FILE"; then
        echo -e "  ${GREEN}✓${NC} SessionStart hook configured"
    else
        echo -e "  ${RED}✗${NC} SessionStart hook NOT configured"
    fi

    if grep -q "pre-bash.py" "$SETTINGS_FILE"; then
        echo -e "  ${GREEN}✓${NC} PreToolUse:Bash hook configured"
    else
        echo -e "  ${YELLOW}!${NC} PreToolUse:Bash hook not configured"
    fi
else
    echo -e "  ${RED}✗${NC} settings.json not found"
fi

# 요약
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Verification Complete${NC}"
echo ""
echo -e "To force sync: ${YELLOW}~/claude-context-engineering/scripts/sync.sh${NC}"
echo -e "To push changes: ${YELLOW}~/claude-context-engineering/scripts/sync.sh --push${NC}"
