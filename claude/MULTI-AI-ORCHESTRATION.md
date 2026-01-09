# MULTI-AI-ORCHESTRATION.md - Cross-Platform AI Coordination

> "Specialists excel at focused execution. Orchestrators coordinate for optimal outcomes."
>
> "Claude for reasoning, Gemini for analysis, Codex for rapid implementation."

Claude Code, Gemini CLI, Codex CLI를 용도에 맞게 호출하여 활용하는 멀티 AI 오케스트레이션 시스템입니다.

## Core Philosophy

```yaml
principles:
  right_tool_for_job: "Match AI strengths to task requirements"
  parallel_when_possible: "Maximize throughput via concurrent execution"
  unified_context: "Shared memory across all AI agents"
  human_oversight: "Orchestrator provides, human approves"
  continuous_evolution: "Learn from multi-agent interactions"
```

## AI Platform Comparison Matrix

```yaml
platforms:
  claude_code:
    strengths:
      - Complex reasoning and planning
      - Code review and refactoring
      - Debugging and root cause analysis
      - System architecture decisions
      - Natural language understanding
    context_window: "200K tokens"
    best_for:
      - Orchestration and coordination
      - Multi-step problem solving
      - Code quality and security review
      - Documentation with reasoning
    mcp_support: true
    local_execution: true

  gemini_cli:
    strengths:
      - Massive context analysis (1M tokens)
      - Visual and UI analysis
      - Broad research synthesis
      - Multimodal understanding
      - Cost-effective analysis
    context_window: "1M+ tokens"
    best_for:
      - Large codebase analysis
      - UI/UX evaluation
      - Comprehensive research
      - Cross-file pattern detection
    free_tier: "1000 requests/day"
    local_execution: true

  codex_cli:
    strengths:
      - Rapid prototyping
      - Code generation speed
      - Framework-specific patterns
      - API integration boilerplate
    context_window: "Variable"
    best_for:
      - Quick code scaffolding
      - Boilerplate generation
      - Framework-specific code
      - Rapid iteration
    local_execution: true
```

## Orchestration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-AI ORCHESTRATION SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      CLAUDE CODE (Primary Orchestrator)                │ │
│   │                                                                        │ │
│   │   - Request analysis and task routing                                  │ │
│   │   - Context management and state preservation                          │ │
│   │   - Result aggregation and synthesis                                   │ │
│   │   - Quality assurance and final verification                          │ │
│   │                                                                        │ │
│   └─────────────────────────────┬─────────────────────────────────────────┘ │
│                                 │                                            │
│                    ┌────────────┼────────────┐                              │
│                    │            │            │                              │
│                    ▼            ▼            ▼                              │
│   ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐       │
│   │   GEMINI CLI     │ │   CODEX CLI      │ │   SPECIALIZED MCPs   │       │
│   │   (Sub-Agent)    │ │   (Sub-Agent)    │ │   (Context7/Magic)   │       │
│   │                  │ │                  │ │                      │       │
│   │ - Large analysis │ │ - Rapid coding   │ │ - Documentation      │       │
│   │ - Visual tasks   │ │ - Prototyping    │ │ - UI components      │       │
│   │ - Research       │ │ - Boilerplate    │ │ - Testing            │       │
│   └──────────────────┘ └──────────────────┘ └──────────────────────┘       │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                    SHARED CONTEXT LAYER                                │ │
│   │                                                                        │ │
│   │   HANDOFF.md    │    .task/*.json    │    .claude/knowledge/          │ │
│   │   (Session)          (Task State)         (Persistent Memory)          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Task Routing Matrix

```yaml
routing_rules:
  route_to_gemini:
    conditions:
      - context_size > 200000  # tokens
      - task_type: "large_codebase_analysis"
      - task_type: "visual_analysis"
      - task_type: "comprehensive_research"
      - task_type: "cross_file_pattern"
    examples:
      - "Analyze this monorepo for code patterns"
      - "Review UI screenshots for consistency"
      - "Research this topic across 50+ files"

  route_to_codex:
    conditions:
      - task_type: "rapid_prototyping"
      - task_type: "boilerplate_generation"
      - task_type: "framework_scaffolding"
      - need_speed: true
    examples:
      - "Generate a REST API scaffold"
      - "Create React component boilerplate"
      - "Quick prototype for testing"

  route_to_claude:
    conditions:
      - task_type: "complex_reasoning"
      - task_type: "code_review"
      - task_type: "architecture_decision"
      - task_type: "debugging"
      - task_type: "security_analysis"
    examples:
      - "Refactor this module for maintainability"
      - "Debug this complex issue"
      - "Design the system architecture"

  route_to_mcp:
    context7:
      - "Library documentation lookup"
      - "Best practices reference"
    magic:
      - "UI component generation"
      - "Design system compliance"
    playwright:
      - "E2E testing"
      - "Visual regression"
```

## Gemini CLI Integration

### Setup

```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Login (uses free tier: 1000 req/day)
gemini login

# Verify installation
gemini --version
```

### Claude Code Integration Patterns

#### Pattern 1: Slash Command Subagent

```markdown
# .claude/commands/gemini.md

---
name: gemini
description: Delegate task to Gemini CLI for large context analysis
---

You are a Gemini CLI orchestrator. When invoked:

1. Prepare the context by gathering relevant files
2. Construct an optimized prompt for Gemini's 1M context
3. Execute: `gemini -p "<prompt>" -f <files>`
4. Parse and synthesize the response
5. Return actionable insights to the user

Use Gemini for:
- Analyzing files that exceed Claude's context window
- Cross-repository pattern detection
- Visual/UI analysis tasks
- Comprehensive research requiring broad context
```

#### Pattern 2: Direct Bash Integration

```bash
# In Claude Code, spawn Gemini for large analysis
gemini -p "Analyze the entire codebase for security vulnerabilities. \
          Provide a detailed report with file locations and severity." \
       -f "src/**/*.ts" "src/**/*.js" \
       --format json > /tmp/gemini-analysis.json

# Read and process results
cat /tmp/gemini-analysis.json
```

#### Pattern 3: Hybrid Workflow

```yaml
hybrid_workflow:
  step_1_claude_plan:
    agent: claude
    action: "Analyze request and create execution plan"
    output: "plan.json"

  step_2_gemini_analyze:
    agent: gemini
    action: "Large-scale codebase analysis"
    input: "Entire codebase context"
    output: "analysis.json"

  step_3_codex_prototype:
    agent: codex
    action: "Rapid prototype based on analysis"
    input: "analysis.json"
    output: "prototype/"

  step_4_claude_refine:
    agent: claude
    action: "Refine prototype with best practices"
    input: "prototype/"
    output: "refined/"

  step_5_claude_verify:
    agent: claude
    action: "Final verification and documentation"
    output: "completed/"
```

## Codex CLI Integration

### Setup

```bash
# Install Codex CLI
npm install -g @openai/codex-cli

# Configure (uses your OpenAI API key)
codex config set api_key $OPENAI_API_KEY

# Trust the project
codex trust /path/to/project
```

### Claude Code Integration Patterns

#### Pattern 1: Rapid Prototyping

```markdown
# .claude/commands/codex-proto.md

---
name: codex-proto
description: Use Codex for rapid prototyping
---

Delegate to Codex for quick code generation:

1. Define the prototype requirements clearly
2. Execute: `codex "Generate a [description]" --output ./prototype/`
3. Review the generated code
4. Refine with Claude for production quality

Best for:
- API scaffolds
- Component boilerplates
- Configuration templates
```

#### Pattern 2: Backend Selection

```bash
# myclaude-style backend selection
# Route to optimal AI based on task

case "$TASK_TYPE" in
  "code_generation")
    codex "$PROMPT" --output "$OUTPUT_DIR"
    ;;
  "reasoning")
    claude "$PROMPT"
    ;;
  "research")
    gemini -p "$PROMPT" -f "$FILES"
    ;;
esac
```

## Dual-Agent Continuous Workflow

### Architecture: Detect-Fix Loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   DUAL-AGENT CONTINUOUS LOOP                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐                      ┌─────────────┐                  │
│   │   GEMINI    │                      │   CLAUDE    │                  │
│   │  (Detector) │                      │   (Fixer)   │                  │
│   │             │                      │             │                  │
│   │  Scans code │────► todo.md ───────►│ Fixes issues│                  │
│   │  for issues │                      │ one by one  │                  │
│   │             │                      │             │                  │
│   └──────┬──────┘                      └──────┬──────┘                  │
│          │                                    │                          │
│          │        ┌─────────────┐            │                          │
│          └───────►│  todo.md    │◄───────────┘                          │
│                   │             │                                        │
│                   │ - ISSUE-001 │ (Gemini adds)                         │
│                   │ - ISSUE-002 │ (Claude fixes, removes)               │
│                   │ - ISSUE-003 │                                       │
│                   └─────────────┘                                        │
│                                                                          │
│   Loop continues until todo.md is empty or max iterations reached        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```bash
#!/bin/bash
# dual-agent-loop.sh

TODO_FILE=".claude/todo.md"
MAX_ITERATIONS=20

# Initialize
echo "# AI-Detected Issues" > $TODO_FILE

for i in $(seq 1 $MAX_ITERATIONS); do
    echo "=== Iteration $i ==="

    # Phase 1: Gemini detects issues
    echo "Gemini scanning for issues..."
    gemini -p "Scan the codebase and append NEW issues to $TODO_FILE. \
               Format: '- [ ] ISSUE-NNN: [description] @[file:line]' \
               Do not duplicate existing issues. \
               Focus on: bugs, security, performance, code quality." \
           -f "src/**/*" \
           >> $TODO_FILE

    # Check if any unchecked items exist
    if ! grep -q "^\- \[ \]" $TODO_FILE; then
        echo "All issues resolved!"
        break
    fi

    # Phase 2: Claude fixes one issue
    echo "Claude fixing next issue..."
    claude "Read $TODO_FILE. Fix the FIRST unchecked issue. \
            After fixing, mark it as completed: '- [x]'. \
            Commit with message referencing the issue ID."

    sleep 5  # Rate limit protection
done
```

## Parallel Agent Execution

### Multi-Worktree Approach

```bash
# Create worktrees for parallel agents
git worktree add ../project-claude-1 main
git worktree add ../project-gemini-1 main
git worktree add ../project-codex-1 main

# Run agents in parallel
(cd ../project-claude-1 && claude "Refactor auth module") &
(cd ../project-gemini-1 && gemini -p "Analyze performance patterns" -f "src/**/*") &
(cd ../project-codex-1 && codex "Generate API tests") &

# Wait for all to complete
wait

# Merge results (human-reviewed)
```

### Claude Squad Integration

```yaml
claude_squad_config:
  instances:
    - name: "architect"
      task: "System design and architecture"
      model: "claude-opus"

    - name: "implementer"
      task: "Code implementation"
      model: "claude-sonnet"

    - name: "reviewer"
      task: "Code review and testing"
      model: "claude-sonnet"

  coordination:
    method: "shared_filesystem"
    sync_file: ".claude/squad-state.json"
```

## Shared Context Management

### Context Synchronization Protocol

```yaml
context_sync:
  handoff_file: ".claude/HANDOFF.md"
  purpose: "Cross-agent state sharing"

  structure:
    current_goal: "Active objective"
    agent_assignments:
      claude: "[Current task]"
      gemini: "[Current task]"
      codex: "[Current task]"
    shared_findings: "Discoveries from all agents"
    blockers: "Issues requiring coordination"

  update_protocol:
    - "Each agent updates after task completion"
    - "Read before starting new task"
    - "Atomic updates to prevent conflicts"
```

### Task State JSON

```json
{
  "task_id": "TASK-001",
  "status": "in_progress",
  "assigned_agent": "gemini",
  "context": {
    "input_files": ["src/**/*.ts"],
    "analysis_type": "security",
    "output_format": "json"
  },
  "results": null,
  "handoff_to": "claude",
  "handoff_instructions": "Review and implement fixes"
}
```

## Evolution and Feedback Loop

### Multi-Agent Retrospective

```yaml
retrospective_protocol:
  per_session:
    - Compare agent routing decisions vs outcomes
    - Measure task completion rates per agent
    - Identify suboptimal routing patterns
    - Track context handoff success rate

  metrics:
    routing_accuracy:
      definition: "Correct agent for task type"
      target: "> 85%"

    handoff_success:
      definition: "Clean context transfer between agents"
      target: "> 95%"

    parallel_efficiency:
      definition: "Actual vs theoretical speedup"
      target: "> 70%"

  evolution_actions:
    - Update routing rules based on performance
    - Refine handoff templates
    - Optimize agent selection criteria
    - Improve context sharing mechanisms
```

### Learning Integration

```yaml
learning_loop:
  capture:
    - Which agent combinations worked best
    - Context sizes that triggered routing
    - Failed handoffs and root causes

  analyze:
    - Pattern recognition in successful workflows
    - Bottleneck identification
    - Cost-efficiency analysis

  apply:
    - Update routing matrix
    - Refine context sync protocol
    - Optimize parallel execution patterns

  validate:
    - A/B test new routing rules
    - Measure improvement metrics
    - Rollback if degradation detected
```

## Quick Reference

### When to Use Each AI

| Task Type | Best Agent | Reason |
|-----------|------------|--------|
| Complex debugging | Claude | Deep reasoning |
| Large codebase analysis | Gemini | 1M token context |
| Rapid prototyping | Codex | Speed |
| Code review | Claude | Quality focus |
| UI/Visual analysis | Gemini | Multimodal |
| Architecture decisions | Claude | Reasoning |
| Boilerplate generation | Codex | Efficiency |
| Research synthesis | Gemini | Broad context |
| Security analysis | Claude | Depth |
| Pattern detection | Gemini | Scale |

### Quick Commands

```bash
# Delegate to Gemini for large analysis
/gemini "Analyze entire codebase for patterns"

# Delegate to Codex for rapid prototyping
/codex-proto "Create REST API scaffold"

# Run dual-agent loop
/dual-loop --detector gemini --fixer claude

# Parallel execution
/parallel-agents --claude "refactor" --gemini "analyze" --codex "test"
```

## References

- [AWS CLI Agent Orchestrator](https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse/)
- [Claude Code Workflow (CCW)](https://github.com/catlog22/Claude-Code-Workflow)
- [Dual-Agent Workflow Pattern](https://medium.com/@slayerfifahamburg/the-dual-agent-workflow-how-to-pair-gemini-cli-and-claude-code-for-autonomous-code-evolution-f8f94900b6fc)
- [Parallel Coding Agents](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/)
- [Gemini CLI as Subagent](https://aicodingtools.blog/en/claude-code/gemini-cli-as-subagent-of-claude-code)
