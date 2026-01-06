#!/bin/bash
#
# continuous-claude.sh - PR Loop 기반 Continuous Claude 실행
#
# Usage:
#   ./scripts/continuous-claude.sh "테스트 커버리지 증가" --max-runs 10
#   ./scripts/continuous-claude.sh "의존성 업그레이드" --pr-loop --auto-merge
#
# Requirements:
#   - claude CLI (authenticated)
#   - gh CLI (authenticated)
#   - jq
#
# References:
#   - https://anandchowdhary.com/blog/2025/running-claude-code-in-a-loop
#   - https://github.com/AnandChowdhary/continuous-claude
#

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Defaults
MAX_RUNS=10
MAX_COST=10
MAX_DURATION="1h"
SLEEP_INTERVAL=5
COMPLETION_SIGNAL="CONTINUOUS_COMPLETE"
COMPLETION_THRESHOLD=3
BRANCH_PREFIX="continuous-claude/"
HANDOFF_FILE=".claude/HANDOFF.md"

# Modes
PR_LOOP=false
AUTO_MERGE=false
DISCARD_ON_FAILURE=true
DRY_RUN=false
VERBOSE=false

# State
RUN_COUNT=0
TOTAL_COST=0.0
CONSECUTIVE_COMPLETIONS=0
START_TIME=$(date +%s)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 <task> [options]

Continuous Claude - PR Loop 기반 자동화

Arguments:
  <task>                    실행할 작업 설명 (필수)

Options:
  --max-runs N              최대 반복 횟수 (default: 10)
  --max-cost N              최대 비용 USD (default: 10)
  --max-duration T          최대 실행 시간 (예: 2h, 30m) (default: 1h)
  --sleep N                 반복 간 대기 시간 초 (default: 5)
  --completion-signal S     완료 신호 문자열 (default: CONTINUOUS_COMPLETE)
  --completion-threshold N  연속 완료 신호 횟수 (default: 3)
  --branch-prefix PREFIX    브랜치 접두사 (default: continuous-claude/)
  --handoff-file PATH       HANDOFF 파일 경로 (default: .claude/HANDOFF.md)

PR Loop Mode:
  --pr-loop                 PR 기반 안전 모드 활성화
  --auto-merge              CI 통과 시 자동 병합
  --no-discard              CI 실패 시 PR 유지 (기본: 폐기)

Other:
  --dry-run                 실제 실행 없이 테스트
  --verbose                 상세 로그 출력
  -h, --help                이 도움말 표시

Examples:
  $0 "테스트 커버리지를 80%까지 높여주세요" --max-runs 20
  $0 "의존성 업그레이드" --pr-loop --auto-merge
  $0 "기술 부채 해결" --max-duration 2h --verbose
EOF
    exit 0
}

check_dependencies() {
    local missing=()

    if ! command -v claude &> /dev/null; then
        missing+=("claude")
    fi

    if ! command -v gh &> /dev/null; then
        missing+=("gh")
    fi

    if ! command -v jq &> /dev/null; then
        missing+=("jq")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        echo "Please install:"
        for dep in "${missing[@]}"; do
            case $dep in
                claude)
                    echo "  - Claude CLI: npm install -g @anthropic/claude-code"
                    ;;
                gh)
                    echo "  - GitHub CLI: https://cli.github.com/"
                    ;;
                jq)
                    echo "  - jq: https://stedolan.github.io/jq/"
                    ;;
            esac
        done
        exit 1
    fi
}

check_git_clean() {
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "Working directory has uncommitted changes"
        if [ "$PR_LOOP" = true ]; then
            log_error "PR Loop mode requires clean working directory"
            exit 1
        fi
    fi
}

parse_duration() {
    local duration=$1
    local seconds=0

    if [[ $duration =~ ^([0-9]+)h$ ]]; then
        seconds=$((${BASH_REMATCH[1]} * 3600))
    elif [[ $duration =~ ^([0-9]+)m$ ]]; then
        seconds=$((${BASH_REMATCH[1]} * 60))
    elif [[ $duration =~ ^([0-9]+)s$ ]]; then
        seconds=${BASH_REMATCH[1]}
    elif [[ $duration =~ ^([0-9]+)$ ]]; then
        seconds=$duration
    fi

    echo $seconds
}

should_continue() {
    # Check run count
    if [ $RUN_COUNT -ge $MAX_RUNS ]; then
        log_info "Maximum runs ($MAX_RUNS) reached"
        return 1
    fi

    # Check duration
    local elapsed=$(($(date +%s) - START_TIME))
    local max_seconds=$(parse_duration "$MAX_DURATION")
    if [ $elapsed -ge $max_seconds ]; then
        log_info "Maximum duration ($MAX_DURATION) reached"
        return 1
    fi

    # Check completion signal threshold
    if [ $CONSECUTIVE_COMPLETIONS -ge $COMPLETION_THRESHOLD ]; then
        log_success "Completion signal received $COMPLETION_THRESHOLD times"
        return 1
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# HANDOFF MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

init_handoff() {
    if [ ! -f "$HANDOFF_FILE" ]; then
        mkdir -p "$(dirname "$HANDOFF_FILE")"
        cat > "$HANDOFF_FILE" << EOF
# Continuous Claude Handoff

## Current Goal

**목표**: $TASK

## Completed in This Run

- (시작 전)

## Next Steps for Next Run

1. 첫 번째 단계 실행

## Progress Metrics

| Metric | Value |
|--------|-------|
| **Run #** | 0 |
| **Started** | $(date +"%Y-%m-%d %H:%M") |
| **Last Updated** | $(date +"%Y-%m-%d %H:%M") |

## Status

**상태**: \`CONTINUING\`
EOF
        log_info "Created HANDOFF.md"
    fi
}

update_handoff_run() {
    if [ -f "$HANDOFF_FILE" ]; then
        sed -i.bak "s/\*\*Run #\*\*.*|.*/\*\*Run #\*\* | $RUN_COUNT/" "$HANDOFF_FILE"
        sed -i.bak "s/\*\*Last Updated\*\*.*|.*/\*\*Last Updated\*\* | $(date +"%Y-%m-%d %H:%M")/" "$HANDOFF_FILE"
        rm -f "$HANDOFF_FILE.bak"
    fi
}

check_completion_signal() {
    if [ -f "$HANDOFF_FILE" ]; then
        if grep -q "$COMPLETION_SIGNAL" "$HANDOFF_FILE"; then
            return 0
        fi
    fi
    return 1
}

# ═══════════════════════════════════════════════════════════════════════════
# STANDARD LOOP
# ═══════════════════════════════════════════════════════════════════════════

run_standard_loop() {
    log_info "Starting Standard Loop"
    init_handoff

    while should_continue; do
        ((RUN_COUNT++))
        update_handoff_run

        log_info "=== Run #$RUN_COUNT ==="

        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would execute: claude -p \"$CLAUDE_PROMPT\""
            sleep 2
        else
            # Run Claude with the prompt
            local output
            output=$(claude --dangerously-skip-permissions -p "$CLAUDE_PROMPT" 2>&1) || true

            if [ "$VERBOSE" = true ]; then
                echo "$output"
            fi

            # Check for completion signal in output
            if echo "$output" | grep -q "$COMPLETION_SIGNAL"; then
                ((CONSECUTIVE_COMPLETIONS++))
                log_info "Completion signal detected ($CONSECUTIVE_COMPLETIONS/$COMPLETION_THRESHOLD)"
            else
                CONSECUTIVE_COMPLETIONS=0
            fi
        fi

        # Check HANDOFF.md for completion
        if check_completion_signal; then
            ((CONSECUTIVE_COMPLETIONS++))
            log_info "Completion signal in HANDOFF.md ($CONSECUTIVE_COMPLETIONS/$COMPLETION_THRESHOLD)"
        fi

        # Sleep between runs
        if should_continue; then
            log_info "Sleeping for $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        fi
    done

    log_success "Loop completed after $RUN_COUNT runs"
}

# ═══════════════════════════════════════════════════════════════════════════
# PR LOOP (SAFE MODE)
# ═══════════════════════════════════════════════════════════════════════════

run_pr_loop() {
    log_info "Starting PR Loop (Safe Mode)"
    init_handoff

    local main_branch
    main_branch=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

    while should_continue; do
        ((RUN_COUNT++))
        update_handoff_run

        log_info "=== PR Loop Run #$RUN_COUNT ==="

        # Create new branch
        local branch_name="${BRANCH_PREFIX}run-$(date +%s)"
        log_info "Creating branch: $branch_name"

        if [ "$DRY_RUN" = false ]; then
            git checkout -b "$branch_name"
        fi

        # Run Claude
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would execute: claude -p \"$CLAUDE_PROMPT\""
            sleep 2
        else
            claude --dangerously-skip-permissions -p "$CLAUDE_PROMPT" || true
        fi

        # Check if there are changes
        if [ "$DRY_RUN" = false ] && [ -z "$(git status --porcelain)" ]; then
            log_warning "No changes made, returning to $main_branch"
            git checkout "$main_branch"
            git branch -D "$branch_name"
            continue
        fi

        # Commit and push
        if [ "$DRY_RUN" = false ]; then
            git add -A
            git commit -m "continuous-claude: Run #$RUN_COUNT

Auto-generated by continuous-claude.sh
Task: $TASK" || true

            git push -u origin "$branch_name"

            # Create PR
            local pr_url
            pr_url=$(gh pr create \
                --title "continuous-claude: Run #$RUN_COUNT" \
                --body "## Auto-generated PR

**Task**: $TASK
**Run**: #$RUN_COUNT

---
*Generated by continuous-claude.sh*" \
                --head "$branch_name" \
                --base "$main_branch")

            log_info "Created PR: $pr_url"

            # Wait for CI
            log_info "Waiting for CI checks..."
            local ci_result
            if gh pr checks "$pr_url" --watch; then
                ci_result="pass"
                log_success "CI checks passed"
            else
                ci_result="fail"
                log_warning "CI checks failed"
            fi

            # Handle CI result
            if [ "$ci_result" = "pass" ]; then
                if [ "$AUTO_MERGE" = true ]; then
                    log_info "Auto-merging PR..."
                    gh pr merge "$pr_url" --squash --delete-branch
                    log_success "PR merged successfully"
                else
                    log_info "PR ready for review: $pr_url"
                fi
            else
                if [ "$DISCARD_ON_FAILURE" = true ]; then
                    log_warning "Discarding failed PR..."
                    gh pr close "$pr_url" --delete-branch
                else
                    log_warning "PR kept for review: $pr_url"
                fi
            fi

            # Return to main branch
            git checkout "$main_branch"
            git pull
        fi

        # Check for completion signal
        if check_completion_signal; then
            ((CONSECUTIVE_COMPLETIONS++))
            log_info "Completion signal detected ($CONSECUTIVE_COMPLETIONS/$COMPLETION_THRESHOLD)"
        else
            CONSECUTIVE_COMPLETIONS=0
        fi

        # Sleep between runs
        if should_continue; then
            log_info "Sleeping for $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        fi
    done

    log_success "PR Loop completed after $RUN_COUNT runs"
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

main() {
    # Parse arguments
    if [ $# -eq 0 ]; then
        usage
    fi

    TASK="$1"
    shift

    while [ $# -gt 0 ]; do
        case "$1" in
            --max-runs)
                MAX_RUNS="$2"
                shift 2
                ;;
            --max-cost)
                MAX_COST="$2"
                shift 2
                ;;
            --max-duration)
                MAX_DURATION="$2"
                shift 2
                ;;
            --sleep)
                SLEEP_INTERVAL="$2"
                shift 2
                ;;
            --completion-signal)
                COMPLETION_SIGNAL="$2"
                shift 2
                ;;
            --completion-threshold)
                COMPLETION_THRESHOLD="$2"
                shift 2
                ;;
            --branch-prefix)
                BRANCH_PREFIX="$2"
                shift 2
                ;;
            --handoff-file)
                HANDOFF_FILE="$2"
                shift 2
                ;;
            --pr-loop)
                PR_LOOP=true
                shift
                ;;
            --auto-merge)
                AUTO_MERGE=true
                shift
                ;;
            --no-discard)
                DISCARD_ON_FAILURE=false
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Build Claude prompt
    CLAUDE_PROMPT="당신은 연속 개발 루프의 일부입니다.

핵심 규칙:
1. HANDOFF.md($HANDOFF_FILE)를 먼저 읽고 이전 진행 상황을 파악하세요
2. 한 번에 하나의 의미 있는 진전만 만드세요
3. 작업 완료 후 HANDOFF.md를 업데이트하세요
4. 모든 목표 달성 시 상태를 $COMPLETION_SIGNAL로 변경하세요

현재 목표: $TASK

시작하기 전에 HANDOFF.md를 읽고 다음 단계를 진행하세요."

    # Checks
    check_dependencies
    check_git_clean

    # Print configuration
    log_info "=== Continuous Claude Configuration ==="
    log_info "Task: $TASK"
    log_info "Max Runs: $MAX_RUNS"
    log_info "Max Duration: $MAX_DURATION"
    log_info "PR Loop: $PR_LOOP"
    log_info "Auto Merge: $AUTO_MERGE"
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No actual execution"
    fi
    echo ""

    # Run appropriate loop
    if [ "$PR_LOOP" = true ]; then
        run_pr_loop
    else
        run_standard_loop
    fi

    # Summary
    local elapsed=$(($(date +%s) - START_TIME))
    local mins=$((elapsed / 60))
    local secs=$((elapsed % 60))

    echo ""
    log_info "=== Summary ==="
    log_info "Total Runs: $RUN_COUNT"
    log_info "Total Time: ${mins}m ${secs}s"
    log_info "Completion Signals: $CONSECUTIVE_COMPLETIONS"
}

main "$@"
