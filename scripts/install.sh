#!/bin/bash
# =============================================================================
# Claude Context-Engineering Installation Script
# =============================================================================
# 최초 설치 또는 완전 재설치 시 사용
#
# 사용법:
#   ./scripts/install.sh
#   ./scripts/install.sh --force   # 기존 파일 무시하고 덮어쓰기
# =============================================================================

set -e  # 오류 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backups/$(date +%Y%m%d_%H%M%S)"

# 플래그 파싱
FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Claude Context-Engineering Installer                      ║"
echo "║     Cross-device synchronization for Claude Code              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. 필수 디렉토리 생성
echo -e "${YELLOW}[1/5]${NC} Creating directories..."
mkdir -p "$CLAUDE_DIR"/{hooks,agents,output-styles,backups}

# 2. 기존 파일 백업
echo -e "${YELLOW}[2/5]${NC} Backing up existing files..."
mkdir -p "$BACKUP_DIR"

backup_if_exists() {
    local src="$1"
    local name="$2"
    if [[ -d "$src" ]] && [[ -n "$(ls -A "$src" 2>/dev/null)" ]]; then
        cp -r "$src" "$BACKUP_DIR/$name" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Backed up $name"
    fi
}

backup_if_exists "$CLAUDE_DIR/hooks" "hooks"
backup_if_exists "$CLAUDE_DIR/agents" "agents"
backup_if_exists "$CLAUDE_DIR/output-styles" "output-styles"

# 3. 파일 동기화 (복사)
echo -e "${YELLOW}[3/5]${NC} Syncing files..."

sync_directory() {
    local src="$1"
    local dst="$2"
    local name="$3"

    if [[ -d "$src" ]] && [[ -n "$(ls -A "$src" 2>/dev/null)" ]]; then
        # 기존 파일 삭제 후 새로 복사 (클린 동기화)
        rm -rf "$dst"/*
        cp -r "$src"/* "$dst/"

        # 실행 권한 설정 (hooks의 .py 파일)
        if [[ "$name" == "hooks" ]]; then
            chmod +x "$dst"/*.py 2>/dev/null || true
        fi

        local count=$(ls -1 "$dst" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} $name: $count files synced"
    else
        echo -e "  ${YELLOW}!${NC} $name: no source files"
    fi
}

sync_directory "$REPO_DIR/hooks" "$CLAUDE_DIR/hooks" "hooks"
sync_directory "$REPO_DIR/agents" "$CLAUDE_DIR/agents" "agents"
sync_directory "$REPO_DIR/output-styles" "$CLAUDE_DIR/output-styles" "output-styles"

# 4. 설정 파일 병합 (hooks 설정만)
echo -e "${YELLOW}[4/5]${NC} Configuring settings.json..."

SETTINGS_FILE="$CLAUDE_DIR/settings.json"
TEMPLATE_FILE="$REPO_DIR/templates/hooks-config.json"

if [[ -f "$TEMPLATE_FILE" ]]; then
    if [[ -f "$SETTINGS_FILE" ]]; then
        # 기존 설정에 hooks 설정만 병합
        # jq가 있으면 사용, 없으면 스킵
        if command -v jq &> /dev/null; then
            cp "$SETTINGS_FILE" "$BACKUP_DIR/settings.json"
            # hooks 키만 업데이트
            jq -s '.[0] * {hooks: .[1].hooks}' "$SETTINGS_FILE" "$TEMPLATE_FILE" > "$SETTINGS_FILE.tmp"
            mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
            echo -e "  ${GREEN}✓${NC} Merged hooks configuration"
        else
            echo -e "  ${YELLOW}!${NC} jq not found, skipping settings merge"
            echo -e "  ${YELLOW}!${NC} Install jq: brew install jq"
        fi
    else
        # 설정 파일이 없으면 템플릿에서 생성
        cp "$TEMPLATE_FILE" "$SETTINGS_FILE"
        echo -e "  ${GREEN}✓${NC} Created settings.json from template"
    fi
else
    echo -e "  ${YELLOW}!${NC} No hooks-config.json template found"
fi

# 5. sync.sh 실행 권한 설정
echo -e "${YELLOW}[5/5]${NC} Setting up sync script..."
chmod +x "$REPO_DIR/scripts/sync.sh" 2>/dev/null || true

# 완료 메시지
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗"
echo -e "║     Installation Complete!                                      ║"
echo -e "╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Backup location: ${BLUE}$BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review ~/.claude/settings.json"
echo "  2. Run 'claude' to start a new session"
echo "  3. Edit files in ~/claude-context-engineering/ to customize"
echo "  4. Use 'git push' to sync changes to other devices"
echo ""
