#!/usr/bin/env python3
"""UserPromptSubmit: Magic Keywords Activation - 매직 키워드 자동 활성화

oh-my-opencode의 keyword-detector + auto-slash-command 패턴 적용:
"ultrawork" 같은 매직 키워드로 전체 기능 자동 활성화

기능:
- 매직 키워드 감지 (ultrawork, ulw, /ultra 등)
- 자동 기능 활성화 (모든 MCP, 모든 플래그)
- 컨텍스트 기반 스마트 활성화
- 작업 유형별 최적 설정 적용
- 다국어 패턴 지원 (한국어, 일본어, 중국어)

지원 키워드:
- ultrawork, ulw, /ultra: 전체 기능 활성화 (TDD, TODO 필수)
- search, find: 병렬 에이전트 검색 모드
- analyze, investigate: 컨텍스트 수집 분석 모드
- deepwork, dw: 깊은 분석 모드
- quickfix, qf: 빠른 수정 모드
- research, rs: 리서치 모드

원본 패턴 (oh-my-opencode):
- ULTRAWORK: Comprehensive task execution + TODO management + TDD + Verification
- SEARCH: Parallel agent deployment (explore + librarian) + direct tools
- ANALYZE: Context-gathering phase before detailed investigation
"""
import json
import os
import re
import sys
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# MULTILINGUAL PATTERNS (oh-my-opencode 원본 패턴)
# ═══════════════════════════════════════════════════════════════════════════

# SEARCH 패턴 - 다국어 지원
SEARCH_PATTERN = re.compile(
    r'(search|find|locate|lookup|explore|discover|scan|grep|query|browse|'
    r'검색|찾|탐색|조회|'  # Korean
    r'検索|探す|調べる|'  # Japanese
    r'搜索|查找|搜|找|'  # Chinese
    r'tìm|tìm kiếm)',  # Vietnamese
    re.IGNORECASE
)

# ANALYZE 패턴 - 다국어 지원
ANALYZE_PATTERN = re.compile(
    r'(analyze|analyse|investigate|examine|research|study|deep.?dive|inspect|audit|debug|comprehend|'
    r'분석|조사|연구|검토|디버그|'  # Korean
    r'分析|調査|研究|検査|デバッグ|'  # Japanese
    r'分析|调查|研究|检查|审计)',  # Chinese
    re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════════════════
# MAGIC KEYWORDS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

MAGIC_KEYWORDS = {
    # === ULTRAWORK: 전체 기능 활성화 (oh-my-opencode 원본 충실) ===
    "ultrawork": {
        "aliases": ["ulw", "/ultra", "/ultrathink", "울트라워크"],
        "pattern": re.compile(r'ultrawork|ulw|/ultra', re.IGNORECASE),
        "description": "모든 기능 최대 활성화 + TODO 필수 + TDD + 검증",
        "activation": {
            "thinking": "--ultrathink",
            "mcp": ["Sequential", "Context7", "Magic", "Playwright"],
            "flags": ["--validate", "--wave-mode auto"],
            "persona": "auto",
        },
        "behavioral_rules": """
## ULTRAWORK Behavioral Rules (oh-my-opencode)

### TODO Management (Non-negotiable)
- **IMMEDIATELY** create detailed todos before starting ANY non-trivial task
- Mark current task `in_progress` BEFORE starting
- Mark `completed` IMMEDIATELY upon finishing (NEVER batch)
- Failure to use todos on multi-step tasks = incomplete work

### TDD Workflow
1. Write failing test first
2. Implement minimum code to pass
3. Refactor while keeping tests green
4. Repeat

### Verification Requirements
| Action | Required Evidence |
|--------|-------------------|
| File edit | LSP diagnostics clean |
| Build command | Exit code 0 |
| Test run | Pass (or note pre-existing failures) |
| Delegation | Agent result verified |

**No evidence = work not complete.**

### Failure Recovery (after 3 consecutive failures)
1. STOP all further edits
2. REVERT to last known working state
3. DOCUMENT what was attempted
4. CONSULT Oracle with full context
5. If unresolved → ASK user
""",
        "message": """
🚀 **ULTRAWORK MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Ultrathink (32K 토큰 깊은 사고)
✓ All MCP Servers (Sequential, Context7, Magic, Playwright)
✓ Wave Orchestration (복잡한 작업 자동 분할)
✓ TODO Non-negotiable (todos 미사용 = 미완료)
✓ TDD Workflow (테스트 먼저)
✓ Verification Required (증거 없음 = 완료 아님)

💡 "Work, delegate, verify, ship. No AI slop."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === DEEPWORK: 깊은 분석 모드 ===
    "deepwork": {
        "aliases": ["dw", "/deep", "딥워크"],
        "description": "깊은 분석 및 아키텍처 설계",
        "activation": {
            "thinking": "--think-hard",
            "mcp": ["Sequential", "Context7"],
            "flags": ["--scope system", "--focus architecture"],
            "persona": "architect",
        },
        "message": """
🔬 **DEEPWORK MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Think-Hard (10K 토큰 시스템 분석)
✓ Sequential + Context7 MCP
✓ Architect Persona Active
✓ System-wide Scope

💡 "Obsess over details. Understand the code's soul."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === QUICKFIX: 빠른 수정 모드 ===
    "quickfix": {
        "aliases": ["qf", "/quick", "퀵픽스"],
        "description": "빠른 버그 수정 및 간단한 변경",
        "activation": {
            "thinking": "--think",
            "mcp": ["Sequential"],
            "flags": ["--uc", "--answer-only"],
            "persona": "analyzer",
        },
        "message": """
⚡ **QUICKFIX MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Focused Thinking (4K 토큰)
✓ Sequential MCP Only
✓ Ultra-compressed Output
✓ Direct Answer Mode

💡 "Fix it fast, fix it right."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === RESEARCH: 리서치 모드 ===
    "research": {
        "aliases": ["rs", "/research", "리서치"],
        "description": "깊은 조사 및 문서화",
        "activation": {
            "thinking": "--think-hard",
            "mcp": ["Context7", "Sequential"],
            "flags": ["--c7", "--verbose"],
            "persona": "mentor",
        },
        "message": """
📚 **RESEARCH MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Deep Research Thinking
✓ Context7 for Documentation
✓ Mentor Persona (지식 전달 최적화)
✓ Verbose Output for Learning

💡 "Evidence > assumptions. Documentation is knowledge."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === SECURITY: 보안 감사 모드 ===
    "security": {
        "aliases": ["sec", "/security", "보안"],
        "description": "보안 취약점 분석 및 감사",
        "activation": {
            "thinking": "--ultrathink",
            "mcp": ["Sequential"],
            "flags": ["--focus security", "--validate", "--safe-mode"],
            "persona": "security",
        },
        "message": """
🛡️ **SECURITY MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Ultrathink for Threat Modeling
✓ Security Persona Active
✓ Safe Mode Enabled
✓ Validation Required

💡 "Zero trust. Verify everything."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === REFACTOR: 리팩토링 모드 ===
    "refactor": {
        "aliases": ["rf", "/refactor", "리팩토링"],
        "description": "코드 품질 개선 및 리팩토링",
        "activation": {
            "thinking": "--think-hard",
            "mcp": ["Sequential", "Context7"],
            "flags": ["--focus quality", "--loop"],
            "persona": "refactorer",
        },
        "message": """
🔧 **REFACTOR MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Code Quality Analysis
✓ Refactorer Persona Active
✓ Iterative Loop Mode
✓ Pattern Recognition via Context7

💡 "Simplify ruthlessly. Elegance = nothing left to remove."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# IMPLICIT MODE DETECTION (oh-my-opencode 원본 패턴)
# ═══════════════════════════════════════════════════════════════════════════

IMPLICIT_MODES = {
    # === SEARCH MODE: 병렬 에이전트 검색 ===
    "search": {
        "pattern": SEARCH_PATTERN,
        "description": "병렬 에이전트 검색 모드",
        "activation": {
            "thinking": "--think",
            "mcp": ["Sequential", "Context7"],
            "flags": ["--delegate auto"],
            "persona": "analyzer",
        },
        "behavioral_rules": """
## SEARCH Mode Rules (oh-my-opencode)

### Parallel Agent Deployment
1. Fire `explore` agent (internal grep): Contextual codebase searches
2. Fire `librarian` agent (external): Official documentation lookups
3. Use direct tools: Grep, ripgrep, ast-grep in parallel

### Search Strategy
- Do NOT block or wait synchronously for explore/librarian results
- Continue immediate work while agents search
- Collect results via background_output when needed
- Before final answer: Cancel all background tasks

### Result Exhaustion
- Search until confident OR 2 iterations yield no new data
- Combine results from all sources
- Prioritize exact matches over fuzzy matches
""",
        "message": """
🔍 **SEARCH MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Parallel Agent Deployment (explore + librarian)
✓ Direct Search Tools (Grep, ripgrep, ast-grep)
✓ Non-blocking Background Search
✓ Result Exhaustion Strategy

💡 "Maximize search effort through concurrent agents."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },

    # === ANALYZE MODE: 컨텍스트 수집 분석 ===
    "analyze": {
        "pattern": ANALYZE_PATTERN,
        "description": "컨텍스트 수집 분석 모드",
        "activation": {
            "thinking": "--think-hard",
            "mcp": ["Sequential", "Context7"],
            "flags": ["--scope project"],
            "persona": "analyzer",
        },
        "behavioral_rules": """
## ANALYZE Mode Rules (oh-my-opencode)

### Context Gathering Phase
1. Fire parallel agents for broad context:
   - `explore` agent for codebase patterns
   - `librarian` agent for external references
2. Perform targeted searches based on initial findings
3. Synthesize findings BEFORE detailed investigation

### Analysis Process
- Map the problem space first
- Identify all relevant files and dependencies
- Understand existing patterns and conventions
- Document assumptions and unknowns

### Codebase Assessment
| State | Signals | Behavior |
|-------|---------|----------|
| Disciplined | Consistent patterns, tests exist | Follow style strictly |
| Transitional | Mixed patterns | Ask: "Which pattern?" |
| Legacy/Chaotic | No consistency | Propose approach first |
| Greenfield | New/empty | Modern best practices |
""",
        "message": """
🔬 **ANALYZE MODE ACTIVATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Parallel Context Gathering
✓ Targeted Search Phase
✓ Finding Synthesis
✓ Codebase Assessment

💡 "Context first, action second."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# KEYWORD DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_magic_keyword(prompt: str) -> tuple[str | None, dict | None, bool]:
    """프롬프트에서 매직 키워드 감지

    Returns:
        (keyword_name, config, is_explicit) 또는 (None, None, False)
        is_explicit: True if explicitly triggered (ultrawork, deepwork, etc.)
                    False if implicitly triggered (search, analyze patterns)
    """
    prompt_lower = prompt.lower().strip()

    # 1. 명시적 키워드 체크 (우선순위 높음)
    for keyword, config in MAGIC_KEYWORDS.items():
        # 패턴이 있으면 패턴 사용
        if "pattern" in config:
            if config["pattern"].search(prompt):
                return keyword, config, True
        else:
            # 메인 키워드 체크
            if keyword in prompt_lower:
                return keyword, config, True

            # 별칭 체크
            for alias in config.get("aliases", []):
                if alias.lower() in prompt_lower:
                    return keyword, config, True

    # 2. 암묵적 모드 체크 (다국어 패턴 기반)
    for mode_name, mode_config in IMPLICIT_MODES.items():
        if mode_config["pattern"].search(prompt):
            return mode_name, mode_config, False

    return None, None, False


def detect_all_modes(prompt: str) -> list[tuple[str, dict, bool]]:
    """프롬프트에서 모든 활성화 가능한 모드 감지 (복합 모드 지원)

    Returns:
        List of (mode_name, config, is_explicit)
    """
    detected = []
    prompt_lower = prompt.lower().strip()

    # 명시적 키워드
    for keyword, config in MAGIC_KEYWORDS.items():
        if "pattern" in config:
            if config["pattern"].search(prompt):
                detected.append((keyword, config, True))
        else:
            if keyword in prompt_lower:
                detected.append((keyword, config, True))
            else:
                for alias in config.get("aliases", []):
                    if alias.lower() in prompt_lower:
                        detected.append((keyword, config, True))
                        break

    # 암묵적 모드 (명시적 키워드가 없을 때만)
    if not detected:
        for mode_name, mode_config in IMPLICIT_MODES.items():
            if mode_config["pattern"].search(prompt):
                detected.append((mode_name, mode_config, False))

    return detected


def remove_keyword_from_prompt(prompt: str, keyword: str, config: dict) -> str:
    """프롬프트에서 키워드 제거 (깔끔한 처리)"""
    result = prompt

    # 메인 키워드 제거
    result = re.sub(rf'\b{keyword}\b', '', result, flags=re.IGNORECASE)

    # 별칭 제거
    for alias in config["aliases"]:
        if alias.startswith('/'):
            result = re.sub(rf'{re.escape(alias)}', '', result, flags=re.IGNORECASE)
        else:
            result = re.sub(rf'\b{alias}\b', '', result, flags=re.IGNORECASE)

    # 연속 공백 정리
    result = re.sub(r'\s+', ' ', result).strip()

    return result


def format_activation_context(config: dict, is_explicit: bool = True) -> str:
    """활성화 컨텍스트 포맷팅

    Args:
        config: 모드 설정
        is_explicit: 명시적 활성화 여부 (암묵적이면 간략한 메시지)
    """
    activation = config["activation"]
    parts = []

    # 활성화 메시지
    parts.append(config["message"])

    # 활성화된 설정 상세
    parts.append("\n**활성화된 설정:**")
    parts.append(f"- Thinking: `{activation['thinking']}`")
    parts.append(f"- MCP: {', '.join(activation['mcp'])}")
    parts.append(f"- Flags: {', '.join(activation['flags'])}")
    parts.append(f"- Persona: {activation['persona']}")

    # 행동 규칙 (명시적 활성화 + behavioral_rules가 있는 경우)
    if is_explicit and "behavioral_rules" in config:
        parts.append("\n" + config["behavioral_rules"])

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════════════════════

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        prompt = input_data.get("prompt", "")

        if not prompt:
            sys.exit(0)

        # 매직 키워드 감지 (명시적 + 암묵적)
        keyword, config, is_explicit = detect_magic_keyword(prompt)

        if keyword and config:
            # 키워드 감지됨!
            activation_context = format_activation_context(config, is_explicit)

            output = {
                "additionalContext": activation_context
            }

            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
