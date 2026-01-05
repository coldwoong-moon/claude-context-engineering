#!/bin/bash
#
# Claude Context Engineering - Research MCP Servers Installation
#
# Usage:
#   ./scripts/install-research-mcp.sh [options]
#
# Options:
#   --all         Install all research MCP servers
#   --semantic    Install Semantic Scholar MCP only
#   --paper       Install Paper Search MCP only
#   --deep        Install Deep Research MCP only
#   --check       Check installation status
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
MCP_DIR="$CLAUDE_DIR/mcp"

log() {
    echo -e "${BOLD}$1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "\n🔍 Checking prerequisites..."

    local missing=0

    # Check Python
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        log_success "Python found"
    else
        log_error "Python not found"
        missing=$((missing + 1))
    fi

    # Check pip
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        log_success "pip found"
    else
        log_error "pip not found"
        missing=$((missing + 1))
    fi

    # Check uv (optional but recommended)
    if command -v uv &> /dev/null; then
        log_success "uv found (recommended)"
    else
        log_warning "uv not found (optional, will use pip)"
    fi

    # Check uvx
    if command -v uvx &> /dev/null; then
        log_success "uvx found"
    else
        log_warning "uvx not found - installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi

    # Check Claude CLI
    if command -v claude &> /dev/null; then
        log_success "Claude CLI found"
    else
        log_error "Claude CLI not found"
        missing=$((missing + 1))
    fi

    # Check git
    if command -v git &> /dev/null; then
        log_success "git found"
    else
        log_error "git not found"
        missing=$((missing + 1))
    fi

    if [ $missing -gt 0 ]; then
        log_error "\nMissing $missing prerequisite(s). Please install them first."
        exit 1
    fi

    log_success "All prerequisites met!"
}

# Install Semantic Scholar MCP
install_semantic_scholar() {
    log "\n📚 Installing Semantic Scholar MCP..."

    # Check if already installed
    local mcp_list=$(claude mcp list 2>/dev/null || echo "")
    if echo "$mcp_list" | grep -q "semantic-scholar"; then
        log_success "Semantic Scholar MCP already installed"
        return 0
    fi

    # Check for API key
    if [ -z "$SEMANTIC_SCHOLAR_API_KEY" ]; then
        log_warning "SEMANTIC_SCHOLAR_API_KEY not set"
        log_info "Get your API key at: https://www.semanticscholar.org/product/api"
        log_info "Set it with: export SEMANTIC_SCHOLAR_API_KEY='your-key'"
        log_info "Installing without API key (limited rate: 100 req/5min)..."
    fi

    # Add MCP server
    claude mcp add semantic-scholar \
        -e SEMANTIC_SCHOLAR_API_KEY="${SEMANTIC_SCHOLAR_API_KEY:-}" \
        -- uvx --from git+https://github.com/FujishigeTemma/semantic-scholar-mcp \
        semantic-scholar-mcp serve \
        && log_success "Semantic Scholar MCP installed" \
        || log_error "Failed to install Semantic Scholar MCP"
}

# Install Paper Search MCP
install_paper_search() {
    log "\n📄 Installing Paper Search MCP..."

    # Check if already installed
    local mcp_list=$(claude mcp list 2>/dev/null || echo "")
    if echo "$mcp_list" | grep -q "paper-search"; then
        log_success "Paper Search MCP already installed"
        return 0
    fi

    # Direct installation via claude mcp add (most reliable)
    install_paper_search_manual
}

install_paper_search_manual() {
    claude mcp add paper-search \
        -e SEMANTIC_SCHOLAR_API_KEY="${SEMANTIC_SCHOLAR_API_KEY:-}" \
        -- uvx --from git+https://github.com/openags/paper-search-mcp \
        python -m paper_search_mcp.server \
        && log_success "Paper Search MCP installed" \
        || log_error "Failed to install Paper Search MCP"
}

# Install Deep Research MCP
install_deep_research() {
    log "\n🔬 Installing Deep Research MCP..."

    # Create MCP directory
    mkdir -p "$MCP_DIR/deep-research"

    # Clone repository
    if [ -d "$MCP_DIR/deep-research/.git" ]; then
        log_info "Updating existing Deep Research installation..."
        git -C "$MCP_DIR/deep-research" pull --ff-only
    else
        log_info "Cloning Deep Research repository..."
        git clone https://github.com/mcherukara/Claude-Deep-Research "$MCP_DIR/deep-research"
    fi

    # Install dependencies
    log_info "Installing dependencies..."
    pip install mcp httpx beautifulsoup4 --quiet

    # Add to Claude (for Desktop)
    log_info "Add this to your Claude Desktop config:"
    echo ""
    echo '  "deep-research": {'
    echo '    "command": "python",'
    echo "    \"args\": [\"$MCP_DIR/deep-research/deep_research.py\"]"
    echo '  }'
    echo ""

    log_success "Deep Research MCP installed"
}

# Check installation status
check_installation() {
    log "\n🔍 Checking Research MCP installation status..."
    echo ""

    # Get MCP list
    local mcp_list=$(claude mcp list 2>/dev/null || echo "")

    # Check each server
    if echo "$mcp_list" | grep -q "semantic-scholar"; then
        log_success "Semantic Scholar MCP: Installed"
    else
        log_warning "Semantic Scholar MCP: Not installed"
    fi

    if echo "$mcp_list" | grep -q "paper-search"; then
        log_success "Paper Search MCP: Installed"
    else
        log_warning "Paper Search MCP: Not installed"
    fi

    if [ -d "$MCP_DIR/deep-research" ]; then
        log_success "Deep Research MCP: Installed"
    else
        log_warning "Deep Research MCP: Not installed"
    fi

    echo ""
    log_info "Run '/research <topic>' in Claude Code to use research mode"
}

# Main installation
install_all() {
    log "\n🚀 Installing Research MCP Servers"
    log "═══════════════════════════════════════════════════"

    check_prerequisites

    install_semantic_scholar
    install_paper_search
    install_deep_research

    log "\n═══════════════════════════════════════════════════"
    log_success "Research MCP installation complete!"

    echo ""
    log_info "Next steps:"
    echo "  1. Set SEMANTIC_SCHOLAR_API_KEY for higher rate limits"
    echo "  2. Restart Claude Code"
    echo "  3. Use /research <topic> to start researching"
    echo ""
    log_info "Documentation: claude/RESEARCH-MODE.md"
}

# Parse arguments
case "${1:-all}" in
    --all|-a)
        install_all
        ;;
    --semantic|-s)
        check_prerequisites
        install_semantic_scholar
        ;;
    --paper|-p)
        check_prerequisites
        install_paper_search
        ;;
    --deep|-d)
        check_prerequisites
        install_deep_research
        ;;
    --check|-c)
        check_installation
        ;;
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --all, -a       Install all research MCP servers (default)"
        echo "  --semantic, -s  Install Semantic Scholar MCP only"
        echo "  --paper, -p     Install Paper Search MCP only"
        echo "  --deep, -d      Install Deep Research MCP only"
        echo "  --check, -c     Check installation status"
        echo "  --help, -h      Show this help"
        ;;
    *)
        install_all
        ;;
esac
