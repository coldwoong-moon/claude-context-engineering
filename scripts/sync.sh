#!/bin/bash
# =============================================================================
# Claude Context-Engineering Sync Script
# =============================================================================
# 세션 시작 시 또는 수동으로 실행하여 GitHub에서 최신 설정을 동기화
#
# 사용법:
#   ./scripts/sync.sh              # 일반 동기화
#   ./scripts/sync.sh --quiet      # 조용한 동기화 (세션 시작용)
#   ./scripts/sync.sh --pull-only  # GitHub에서만 pull (로컬 변경 무시)
#   ./scripts/sync.sh --push       # 로컬 변경을 GitHub에 push
# =============================================================================

set -e  # 오류 시 즉시 종료

# 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
LOCK_FILE="/tmp/claude-context-sync.lock"
LOG_FILE="$HOME/.claude/logs/sync.log"

# 플래그 파싱
QUIET=false
PULL_ONLY=false
PUSH=false

for arg in "$@"; do
    case $arg in
        --quiet)
            QUIET=true
            ;;
        --pull-only)
            PULL_ONLY=true
            ;;
        --push)
            PUSH=true
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

# 동시 실행 방지 (락 파일)
if [[ -f "$LOCK_FILE" ]]; then
    # 5분 이상된 락 파일은 삭제
    if [[ $(find "$LOCK_FILE" -mmin +5 2>/dev/null) ]]; then
        rm -f "$LOCK_FILE"
    else
        log "Sync already in progress, skipping"
        exit 0
    fi
fi

# 락 설정
trap "rm -f $LOCK_FILE" EXIT
touch "$LOCK_FILE"

# 저장소 존재 확인
if [[ ! -d "$REPO_DIR/.git" ]]; then
    log "ERROR: Not a git repository: $REPO_DIR"
    exit 1
fi

cd "$REPO_DIR"

# Push 모드
if [[ "$PUSH" == true ]]; then
    log "Pushing local changes to GitHub..."

    # 로컬 변경 사항 확인
    if [[ -n $(git status --porcelain) ]]; then
        git add -A
        git commit -m "sync: Update context-engineering $(date '+%Y-%m-%d %H:%M')"
        git push origin main
        log "Successfully pushed changes"
    else
        log "No changes to push"
    fi
    exit 0
fi

# Pull 모드 (기본)
log "Syncing from GitHub..."

# 1. GitHub에서 pull
if git remote get-url origin &> /dev/null; then
    # fetch 먼저 (오류 확인용)
    if git fetch origin main --quiet 2>/dev/null; then
        # 로컬 변경 사항이 있으면 stash
        if [[ -n $(git status --porcelain) ]] && [[ "$PULL_ONLY" == false ]]; then
            git stash push -m "Auto-stash before sync"
            STASHED=true
        fi

        # pull (fast-forward only)
        git pull --ff-only origin main --quiet 2>/dev/null || {
            log "WARN: Could not fast-forward, manual intervention needed"
            if [[ "$STASHED" == true ]]; then
                git stash pop --quiet
            fi
            exit 0
        }

        # stash 복구
        if [[ "$STASHED" == true ]]; then
            git stash pop --quiet || true
        fi
    else
        log "WARN: Could not fetch from origin, using local files"
    fi
else
    log "WARN: No remote configured"
fi

# 2. 파일 동기화
sync_to_claude() {
    local src="$1"
    local dst="$2"

    if [[ -d "$src" ]] && [[ -n "$(ls -A "$src" 2>/dev/null)" ]]; then
        mkdir -p "$dst"
        # rsync가 있으면 사용, 없으면 cp
        if command -v rsync &> /dev/null; then
            rsync -a --delete "$src/" "$dst/"
        else
            rm -rf "$dst"/*
            cp -r "$src"/* "$dst/"
        fi

        # hooks는 실행 권한 설정
        if [[ "$dst" == *"/hooks"* ]]; then
            chmod +x "$dst"/*.py 2>/dev/null || true
        fi
    fi
}

sync_to_claude "$REPO_DIR/hooks" "$CLAUDE_DIR/hooks"
sync_to_claude "$REPO_DIR/agents" "$CLAUDE_DIR/agents"
sync_to_claude "$REPO_DIR/output-styles" "$CLAUDE_DIR/output-styles"

log "Sync completed successfully"
