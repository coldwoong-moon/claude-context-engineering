#!/bin/bash
# Claude Context Engineering 구조 검증 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$REPO_DIR/claude"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 버전 읽기
VERSION="unknown"
if [[ -f "$REPO_DIR/VERSION" ]]; then
    VERSION=$(cat "$REPO_DIR/VERSION" | tr -d '[:space:]')
fi

echo "═══════════════════════════════════════════════════════"
echo "  Claude Context Engineering 검증 (v$VERSION)"
echo "═══════════════════════════════════════════════════════"
echo ""

ERRORS=0
WARNINGS=0

# 1. Python Hook 문법 검증
echo "📋 Python Hook 검증..."
for hook in "$CLAUDE_DIR"/hooks/*.py; do
    if python3 -m py_compile "$hook" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $(basename "$hook")"
    else
        echo -e "  ${RED}❌${NC} $(basename "$hook") - 문법 오류"
        ((ERRORS++))
    fi
done
echo ""

# 2. JSON 파일 검증
echo "📋 JSON 설정 검증..."
for json in "$CLAUDE_DIR"/templates/*.json "$CLAUDE_DIR"/settings.json; do
    if [ -f "$json" ]; then
        if python3 -c "import json; json.load(open('$json'))" 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} $(basename "$json")"
        else
            echo -e "  ${RED}❌${NC} $(basename "$json") - JSON 오류"
            ((ERRORS++))
        fi
    fi
done
echo ""

# 3. Markdown 파일 존재 확인
echo "📋 Agent/Output Style 검증..."
for md in "$CLAUDE_DIR"/agents/*.md "$CLAUDE_DIR"/output-styles/*.md; do
    if [ -f "$md" ]; then
        if head -1 "$md" | grep -q "^---"; then
            echo -e "  ${GREEN}✅${NC} $(basename "$md") (frontmatter OK)"
        else
            echo -e "  ${YELLOW}⚠️${NC} $(basename "$md") - frontmatter 없음"
            ((WARNINGS++))
        fi
    fi
done
echo ""

# 4. 필수 파일 확인
echo "📋 필수 파일 확인..."
REQUIRED_FILES=(
    "hooks/session-start.py"
    "hooks/pre-bash.py"
    "hooks/utils.py"
    "agents/task-worker.md"
    "templates/settings-core.json"
    "README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$CLAUDE_DIR/$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file - 누락"
        ((ERRORS++))
    fi
done
echo ""

# 5. 통계
echo "═══════════════════════════════════════════════════════"
echo "  통계"
echo "═══════════════════════════════════════════════════════"
echo "  Hooks:        $(ls "$CLAUDE_DIR"/hooks/*.py 2>/dev/null | wc -l | tr -d ' ') files"
echo "  Agents:       $(ls "$CLAUDE_DIR"/agents/*.md 2>/dev/null | wc -l | tr -d ' ') files"
echo "  Output Styles: $(ls "$CLAUDE_DIR"/output-styles/*.md 2>/dev/null | wc -l | tr -d ' ') files"
echo "  Templates:    $(ls "$CLAUDE_DIR"/templates/*.json 2>/dev/null | wc -l | tr -d ' ') files"
echo ""

# 결과 출력
echo "═══════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "  ${GREEN}✅ 모든 검증 통과${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "  ${YELLOW}⚠️ 경고 $WARNINGS개 (오류 없음)${NC}"
else
    echo -e "  ${RED}❌ 오류 $ERRORS개, 경고 $WARNINGS개${NC}"
fi
echo "═══════════════════════════════════════════════════════"

exit $ERRORS
