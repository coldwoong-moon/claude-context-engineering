#!/bin/bash
# =============================================================================
# AI Tools Context-Engineering Verification Script
# =============================================================================
# Claude Code, Gemini CLI, Codex 동기화 상태를 확인합니다.
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
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
GEMINI_DIR="$HOME/.gemini"
CODEX_DIR="$HOME/.codex"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     AI Tools Context-Engineering Verification                 ║"
echo "║     Claude Code | Gemini CLI | Codex                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. Repository 상태
echo -e "${YELLOW}[1/7]${NC} Repository Status"
if [[ -d "$REPO_DIR/.git" ]]; then
    VERSION=$(cat "$REPO_DIR/VERSION" 2>/dev/null || echo "unknown")
    COMMIT=$(git -C "$REPO_DIR" log -1 --format="%h %s" 2>/dev/null || echo "unknown")
    echo -e "  ${GREEN}✓${NC} Repository: $REPO_DIR"
    echo -e "  ${GREEN}✓${NC} Version: $VERSION"
    echo -e "  ${GREEN}✓${NC} Latest commit: $COMMIT"
else
    echo -e "  ${RED}✗${NC} Repository not found at $REPO_DIR"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Claude Code
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${CYAN}═══ Claude Code ═══${NC}"

# 2. Claude Hooks 동기화
echo -e "${YELLOW}[2/7]${NC} Claude Hooks"
for hook in session-start.py pre-bash.py post-bash.py pre-edit.py post-edit.py stop.py; do
    REPO_FILE="$REPO_DIR/claude/hooks/$hook"
    LOCAL_FILE="$CLAUDE_DIR/hooks/$hook"

    if [[ -f "$REPO_FILE" ]] && [[ -f "$LOCAL_FILE" ]]; then
        if diff -q "$REPO_FILE" "$LOCAL_FILE" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $hook - synced"
        else
            echo -e "  ${YELLOW}!${NC} $hook - differs"
        fi
    elif [[ -f "$REPO_FILE" ]]; then
        echo -e "  ${RED}✗${NC} $hook - not installed"
    fi
done

# 3. Claude Agents
echo -e "\n${YELLOW}[3/7]${NC} Claude Agents"
REPO_AGENTS=$(ls -1 "$REPO_DIR/claude/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
LOCAL_AGENTS=$(ls -1 "$CLAUDE_DIR/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo -e "  Repository: $REPO_AGENTS agents"
echo -e "  Installed:  $LOCAL_AGENTS agents"

# 4. Claude Plugins
echo -e "\n${YELLOW}[4/7]${NC} Claude Plugins"
if [[ -f "$CLAUDE_DIR/settings.json" ]] && command -v jq &> /dev/null; then
    ENABLED=$(jq '.enabledPlugins | to_entries | map(select(.value == true)) | length' "$CLAUDE_DIR/settings.json" 2>/dev/null || echo "0")
    echo -e "  ${GREEN}✓${NC} $ENABLED plugins enabled"
else
    echo -e "  ${YELLOW}!${NC} Could not check plugins (jq required)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Gemini CLI
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${CYAN}═══ Gemini CLI ═══${NC}"

echo -e "${YELLOW}[5/7]${NC} Gemini Status"
if [[ -d "$GEMINI_DIR" ]]; then
    if [[ -f "$GEMINI_DIR/settings.json" ]]; then
        echo -e "  ${GREEN}✓${NC} settings.json exists"
    else
        echo -e "  ${YELLOW}!${NC} settings.json not found"
    fi

    if [[ -d "$GEMINI_DIR/extensions" ]]; then
        EXT_COUNT=$(ls -1 "$GEMINI_DIR/extensions" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} $EXT_COUNT extensions installed"
    fi
else
    echo -e "  ${YELLOW}!${NC} Gemini CLI not installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Codex
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${CYAN}═══ Codex ═══${NC}"

echo -e "${YELLOW}[6/7]${NC} Codex Status"
if [[ -d "$CODEX_DIR" ]]; then
    if [[ -f "$CODEX_DIR/config.toml" ]]; then
        MODEL=$(grep "^model = " "$CODEX_DIR/config.toml" 2>/dev/null | cut -d'"' -f2 || echo "unknown")
        echo -e "  ${GREEN}✓${NC} config.toml exists (model: $MODEL)"
    else
        echo -e "  ${YELLOW}!${NC} config.toml not found"
    fi

    if [[ -d "$CODEX_DIR/prompts" ]]; then
        PROMPT_COUNT=$(ls -1 "$CODEX_DIR/prompts"/*.md 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} $PROMPT_COUNT prompts installed"
    fi

    if [[ -d "$CODEX_DIR/skills" ]]; then
        SKILL_COUNT=$(ls -1 "$CODEX_DIR/skills" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} $SKILL_COUNT skills installed"
    fi
else
    echo -e "  ${YELLOW}!${NC} Codex not installed"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Sync Log
# ═══════════════════════════════════════════════════════════════════════════
echo -e "\n${YELLOW}[7/7]${NC} Recent Sync Activity"
LOG_FILE="$CLAUDE_DIR/logs/sync.log"
if [[ -f "$LOG_FILE" ]]; then
    LAST_SYNC=$(tail -1 "$LOG_FILE")
    SYNC_COUNT=$(wc -l < "$LOG_FILE" | tr -d ' ')
    echo -e "  ${GREEN}✓${NC} Log: $SYNC_COUNT entries"
    echo -e "  ${GREEN}✓${NC} Last: $LAST_SYNC"
else
    echo -e "  ${YELLOW}!${NC} No sync log found"
fi

# 요약
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Verification Complete${NC}"
echo ""
echo -e "Commands:"
echo -e "  ${YELLOW}~/claude-context-engineering/scripts/sync.sh${NC}          # Sync all"
echo -e "  ${YELLOW}~/claude-context-engineering/scripts/sync.sh --claude${NC}  # Claude only"
echo -e "  ${YELLOW}~/claude-context-engineering/scripts/sync.sh --gemini${NC}  # Gemini only"
echo -e "  ${YELLOW}~/claude-context-engineering/scripts/sync.sh --codex${NC}   # Codex only"
echo -e "  ${YELLOW}~/claude-context-engineering/scripts/sync.sh --push${NC}    # Push changes"
