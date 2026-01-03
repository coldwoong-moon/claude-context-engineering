#!/bin/bash
# =============================================================================
# AI Tools Context-Engineering Sync Script
# =============================================================================
# Claude Code, Gemini CLI, Codex 설정을 GitHub에서 동기화
#
# 사용법:
#   ./scripts/sync.sh              # 일반 동기화 (모든 도구)
#   ./scripts/sync.sh --quiet      # 조용한 동기화 (세션 시작용)
#   ./scripts/sync.sh --push       # 로컬 변경을 GitHub에 push
#   ./scripts/sync.sh --claude     # Claude만 동기화
#   ./scripts/sync.sh --gemini     # Gemini만 동기화
#   ./scripts/sync.sh --codex      # Codex만 동기화
# =============================================================================

set -e

# 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
GEMINI_DIR="$HOME/.gemini"
CODEX_DIR="$HOME/.codex"
LOCK_FILE="/tmp/ai-context-sync.lock"
LOG_FILE="$HOME/.claude/logs/sync.log"

# 플래그 파싱
QUIET=false
PUSH=false
SYNC_CLAUDE=true
SYNC_GEMINI=true
SYNC_CODEX=true

for arg in "$@"; do
    case $arg in
        --quiet)
            QUIET=true
            ;;
        --push)
            PUSH=true
            ;;
        --claude)
            SYNC_GEMINI=false
            SYNC_CODEX=false
            ;;
        --gemini)
            SYNC_CLAUDE=false
            SYNC_CODEX=false
            ;;
        --codex)
            SYNC_CLAUDE=false
            SYNC_GEMINI=false
            ;;
    esac
done

# 로그 함수
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$msg" >> "$LOG_FILE"
    if [[ "$QUIET" == false ]]; then
        echo "$msg"
    fi
}

# 동시 실행 방지
if [[ -f "$LOCK_FILE" ]]; then
    if [[ $(find "$LOCK_FILE" -mmin +5 2>/dev/null) ]]; then
        rm -f "$LOCK_FILE"
    else
        log "Sync already in progress, skipping"
        exit 0
    fi
fi

trap "rm -f $LOCK_FILE" EXIT
touch "$LOCK_FILE"

# 저장소 확인
if [[ ! -d "$REPO_DIR/.git" ]]; then
    log "ERROR: Not a git repository: $REPO_DIR"
    exit 1
fi

cd "$REPO_DIR"

# Push 모드
if [[ "$PUSH" == true ]]; then
    log "Pushing local changes to GitHub..."

    if [[ -n $(git status --porcelain) ]]; then
        git add -A
        git commit -m "sync: Update AI tools config $(date '+%Y-%m-%d %H:%M')"
        git push origin main
        log "Successfully pushed changes"
    else
        log "No changes to push"
    fi
    exit 0
fi

# Pull 모드 (기본)
log "Syncing from GitHub..."

if git remote get-url origin &> /dev/null; then
    if git fetch origin main --quiet 2>/dev/null; then
        if [[ -n $(git status --porcelain) ]]; then
            git stash push -m "Auto-stash before sync" --quiet 2>/dev/null || true
            STASHED=true
        fi

        git pull --ff-only origin main --quiet 2>/dev/null || {
            log "WARN: Could not fast-forward, manual intervention needed"
            [[ "$STASHED" == true ]] && git stash pop --quiet 2>/dev/null || true
            exit 0
        }

        [[ "$STASHED" == true ]] && git stash pop --quiet 2>/dev/null || true
    else
        log "WARN: Could not fetch from origin, using local files"
    fi
fi

# 디렉토리 동기화 함수
sync_dir() {
    local src="$1"
    local dst="$2"

    if [[ -d "$src" ]] && [[ -n "$(ls -A "$src" 2>/dev/null)" ]]; then
        mkdir -p "$dst"
        if command -v rsync &> /dev/null; then
            rsync -a --delete "$src/" "$dst/"
        else
            rm -rf "$dst"/* 2>/dev/null || true
            cp -r "$src"/* "$dst/"
        fi

        # hooks는 실행 권한 설정
        if [[ "$dst" == *"/hooks"* ]]; then
            chmod +x "$dst"/*.py 2>/dev/null || true
        fi
    fi
}

# 파일 동기화 함수 (단일 파일, 병합)
sync_file() {
    local src="$1"
    local dst="$2"

    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dst")"
        cp "$src" "$dst"
    fi
}

# JSON 병합 함수 (jq 필요)
merge_json() {
    local src="$1"
    local dst="$2"

    if [[ -f "$src" ]] && command -v jq &> /dev/null; then
        if [[ -f "$dst" ]]; then
            # 기존 파일에 새 설정 병합
            jq -s '.[0] * .[1]' "$dst" "$src" > "$dst.tmp" && mv "$dst.tmp" "$dst"
        else
            cp "$src" "$dst"
        fi
    fi
}

# TOML 병합 함수 (model/model_reasoning_effort만)
merge_toml() {
    local src="$1"
    local dst="$2"

    if [[ -f "$src" ]]; then
        if [[ -f "$dst" ]]; then
            # 기존 파일에서 model 관련 라인만 교체
            local model_line=$(grep "^model = " "$src" 2>/dev/null || true)
            local effort_line=$(grep "^model_reasoning_effort = " "$src" 2>/dev/null || true)

            if [[ -n "$model_line" ]]; then
                if grep -q "^model = " "$dst"; then
                    sed -i.bak "s|^model = .*|$model_line|" "$dst"
                else
                    echo "$model_line" >> "$dst"
                fi
            fi

            if [[ -n "$effort_line" ]]; then
                if grep -q "^model_reasoning_effort = " "$dst"; then
                    sed -i.bak "s|^model_reasoning_effort = .*|$effort_line|" "$dst"
                else
                    echo "$effort_line" >> "$dst"
                fi
            fi
            rm -f "$dst.bak"
        else
            cp "$src" "$dst"
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Claude Code 동기화
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$SYNC_CLAUDE" == true ]]; then
    log "Syncing Claude Code..."
    sync_dir "$REPO_DIR/claude/hooks" "$CLAUDE_DIR/hooks"
    sync_dir "$REPO_DIR/claude/agents" "$CLAUDE_DIR/agents"
    sync_dir "$REPO_DIR/claude/output-styles" "$CLAUDE_DIR/output-styles"

    # settings.json 병합 (enabledPlugins, hooks만)
    if [[ -f "$REPO_DIR/claude/settings.json" ]] && command -v jq &> /dev/null; then
        if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
            # 백업
            cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.sync-backup"
            # enabledPlugins와 hooks만 병합
            jq -s '.[0] * {enabledPlugins: .[1].enabledPlugins, hooks: .[1].hooks}' \
                "$CLAUDE_DIR/settings.json" "$REPO_DIR/claude/settings.json" \
                > "$CLAUDE_DIR/settings.json.tmp" && \
                mv "$CLAUDE_DIR/settings.json.tmp" "$CLAUDE_DIR/settings.json"
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# Gemini CLI 동기화
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$SYNC_GEMINI" == true ]] && [[ -d "$GEMINI_DIR" ]]; then
    log "Syncing Gemini CLI..."
    sync_file "$REPO_DIR/gemini/settings.json" "$GEMINI_DIR/settings.json"
    sync_dir "$REPO_DIR/gemini/extensions" "$GEMINI_DIR/extensions"

    if [[ -f "$REPO_DIR/gemini/GEMINI.md" ]]; then
        cp "$REPO_DIR/gemini/GEMINI.md" "$GEMINI_DIR/GEMINI.md"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# Codex 동기화
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$SYNC_CODEX" == true ]] && [[ -d "$CODEX_DIR" ]]; then
    log "Syncing Codex..."
    merge_toml "$REPO_DIR/codex/config.toml" "$CODEX_DIR/config.toml"
    sync_dir "$REPO_DIR/codex/prompts" "$CODEX_DIR/prompts"
    sync_dir "$REPO_DIR/codex/skills" "$CODEX_DIR/skills"
fi

log "Sync completed successfully"
