# ORCHESTRATOR-AGENTS.md - Sisyphus-Style Agent Orchestration

oh-my-opencode의 Sisyphus 패턴을 SuperClaude에 적용한 에이전트 오케스트레이션 시스템.

## Core Philosophy

```
"Work, delegate, verify, ship. No AI slop."
- Never work alone when specialists exist
- Extract implicit requirements from explicit requests
- Execute tasks in parallel for maximum throughput
- NEVER start implementing unless explicitly requested
```

## Phased Execution Model (oh-my-opencode 원본)

### Phase 0: Intent Gate (Blocking)
```yaml
trigger: Before any classification
action: Scan for matching skill triggers
behavior:
  - If skill match found → Invoke skill tool IMMEDIATELY
  - Do NOT proceed until skill completes
  - This phase BLOCKS all other processing
```

### Phase 1: Request Classification
```yaml
types:
  skill_match:
    signal: "Matches skill trigger phrase"
    action: "Invoke skill via tool"

  trivial:
    signal: "Single file, known location"
    action: "Direct tools only"

  explicit:
    signal: "Specific file/line, clear command"
    action: "Execute directly"

  exploratory:
    signal: "'How does X work?', 'Find Y'"
    action: "Fire explores (1-3) + tools in parallel"

  open_ended:
    signal: "'Improve', 'Refactor', 'Add feature'"
    action: "Assess codebase first"

  github_work:
    signal: "Mentioned in issues/PRs"
    action: "Full cycle: investigate → implement → verify → create PR"
```

### Phase 2: Ambiguity Check
```yaml
rules:
  single_interpretation: "Proceed"
  multiple_similar_effort: "Proceed with reasonable default, note assumptions"
  multiple_2x_effort_diff: "MUST ask"
  missing_critical_info: "MUST ask"
  flawed_design: "Raise concern BEFORE implementing"
```

### Phase 2B: Pre-Implementation
```yaml
todo_management:
  - Create detailed todo IMMEDIATELY (no announcements)
  - Mark current task `in_progress` BEFORE starting
  - Mark `completed` IMMEDIATELY upon finishing (NEVER batch)
  - Update todos if scope changes

anti_patterns:
  - Skipping todos on multi-step tasks → user loses visibility
  - Batch-completing todos → defeats real-time tracking
  - Proceeding without marking in_progress → no indication of focus
  - Finishing without completing todos → task appears incomplete

failure_consequence: "Failure to use todos on non-trivial tasks = incomplete work"
```

### Phase 2C: Failure Recovery
```yaml
trigger: "After 3 consecutive failures"
steps:
  1: "STOP all further edits immediately"
  2: "REVERT to last known working state"
  3: "DOCUMENT what was attempted and what failed"
  4: "CONSULT Oracle with full failure context"
  5: "If Oracle cannot resolve → ASK user before proceeding"

critical_rule: "Never leave code in broken state; never continue with random changes"
```

### Phase 3: Validation Before Acting
```yaml
verification_requirements:
  file_edit: "LSP diagnostics clean on changed files"
  build_command: "Exit code 0"
  test_run: "Pass (or note pre-existing failures)"
  delegation: "Agent result received and verified"

golden_rule: "No evidence = work not complete"
```

## Agent Hierarchy

### Primary Orchestrator: Sisyphus

**Identity**: AI 오케스트레이터 - 반복 작업을 처리하는 신화적 인물에서 영감

**Core Competencies**:
- 명시적 요청에서 암묵적 요구사항 추출
- 코드베이스 성숙도에 따른 적응
- 전문가 서브에이전트에게 작업 위임
- 최대 처리량을 위한 병렬 실행
- 사용자 지시 없이 스스로 작업 시작 금지

**Operating Principle**:
```yaml
delegation_rules:
  - frontend_tasks → Frontend Engineer (Magic MCP)
  - deep_research → Oracle (Sequential MCP)
  - documentation → Librarian (Context7 MCP)
  - security_audit → Security Specialist (Sequential MCP)
  - complex_architecture → Architect Consultation
```

### Specialist Agents

#### Oracle - Deep Research Consultant
```yaml
role: "심층 연구 및 아키텍처 자문"
model: claude-opus-4-5
activation:
  - Complex architectural questions
  - System-wide analysis needs
  - Critical decision points
mcp_integration:
  - Sequential (primary)
  - Context7 (documentation)
```

#### Frontend Engineer - UI/UX Specialist
```yaml
role: "UI 컴포넌트 및 사용자 경험"
model: claude-sonnet-4
activation:
  - Component creation requests
  - Responsive design needs
  - Accessibility requirements
mcp_integration:
  - Magic (primary)
  - Playwright (testing)
```

#### Librarian - Evidence-Based Research
```yaml
role: "증거 기반 연구 및 문서화"
model: claude-haiku-3-5
activation:
  - Documentation requests
  - Library research
  - Best practices lookup
mcp_integration:
  - Context7 (primary)
  - Sequential (structured analysis)
```

#### Security Specialist
```yaml
role: "보안 분석 및 취약점 평가"
model: claude-opus-4-5
activation:
  - Security audit requests
  - Vulnerability assessment
  - Threat modeling
mcp_integration:
  - Sequential (threat modeling)
  - Context7 (security patterns)
```

## Delegation Protocol (7 Mandatory Sections - oh-my-opencode)

### Delegation Prompt Structure
```yaml
mandatory_sections:
  1_TASK: "Atomic, specific goal"
  2_EXPECTED_OUTCOME: "Concrete deliverables with success criteria"
  3_REQUIRED_SKILLS: "Which specialized skill to invoke"
  4_REQUIRED_TOOLS: "Explicit whitelist (prevents tool sprawl)"
  5_MUST_DO: "Exhaustive requirements (nothing implicit)"
  6_MUST_NOT_DO: "Forbidden actions, anticipated rogue behavior"
  7_CONTEXT: "File paths, patterns, constraints"

post_delegation: "Always verify results against expected outcome and existing patterns"
```

### Example Delegation
```markdown
## TASK
Implement user authentication endpoint

## EXPECTED OUTCOME
- POST /api/auth/login endpoint
- JWT token generation
- Password hashing with bcrypt
- Success: 200 + token, Failure: 401

## REQUIRED SKILLS
Backend API development

## REQUIRED TOOLS
- Read (existing auth patterns)
- Write (new endpoint)
- Bash (run tests)

## MUST DO
- Follow existing error handling pattern in src/utils/errors.ts
- Use existing User model from src/models/user.ts
- Add validation middleware

## MUST NOT DO
- Create new dependencies
- Modify existing endpoints
- Skip input validation

## CONTEXT
- Auth patterns: src/middleware/auth.ts
- Route patterns: src/routes/index.ts
- Project uses Express + TypeScript
```

## Codebase Assessment (oh-my-opencode)

### State Classification
```yaml
disciplined:
  signals:
    - Consistent patterns
    - Configs present
    - Tests exist
  behavior: "Follow existing style STRICTLY"

transitional:
  signals:
    - Mixed patterns
    - Some structure
  behavior: "Ask: 'Which pattern to follow?'"

legacy_chaotic:
  signals:
    - No consistency
    - Outdated patterns
  behavior: "Propose: 'I suggest [approach]. OK?'"

greenfield:
  signals:
    - New/empty project
  behavior: "Apply modern best practices"
```

### Assessment Process
```yaml
steps:
  1: "Scan for config files (tsconfig, eslint, prettier, etc.)"
  2: "Check for test directories and coverage"
  3: "Identify dominant patterns in 3-5 key files"
  4: "Classify state based on signals"
  5: "Adjust behavior accordingly"
```

## Parallel Execution Strategy

### Default Behavior
```yaml
parallel_agents:
  explore:
    type: "Internal grep"
    purpose: "Contextual codebase searches"
    blocking: false

  librarian:
    type: "External lookup"
    purpose: "Official documentation"
    blocking: false

  frontend_engineer:
    type: "UI specialist"
    purpose: "Visual changes"
    blocking: false

rule: "Do NOT block or wait synchronously for explore/librarian results"
```

### Background Result Collection
```yaml
workflow:
  1: "Launch parallel agents → receive task_ids"
  2: "Continue immediate work"
  3: "Collect results via background_output(task_id=...) when needed"
  4: "Before final answer: background_cancel(all=true)"
```

## Integration with SuperClaude

### Persona Mapping
```yaml
sisyphus_to_supercloud:
  Oracle: "--persona-architect + --ultrathink"
  Frontend Engineer: "--persona-frontend + --magic"
  Librarian: "--persona-scribe + --c7"
  Security Specialist: "--persona-security + --think-hard"
```

### MCP Integration
```yaml
agent_mcp_preferences:
  primary_orchestrator:
    - Sequential (coordination)
    - All servers (as needed)

  oracle:
    - Sequential (deep analysis)
    - Context7 (patterns)

  frontend_engineer:
    - Magic (UI generation)
    - Playwright (testing)

  librarian:
    - Context7 (documentation)
    - Sequential (structure)
```

### Hook Integration
```yaml
hook_triggers:
  SubagentStop:
    - continuation-enforcer.py
    - Check incomplete tasks
    - Enforce work completion

  Stop:
    - continuation-enforcer.py
    - Session reflection
    - State preservation
```

## Continuation Enforcement

### Never Stop Principle
```python
CONTINUATION_RULES = {
    "incomplete_todos": "Continue to next task",
    "in_progress_work": "Complete current task",
    "blocked_tasks": "Report blocker, suggest alternatives",
    "user_interruption": "Only stop on explicit user request",
}
```

### State Tracking
```yaml
session_state:
  - Current task (in_progress)
  - Pending tasks (queued)
  - Completed tasks (today)
  - Blocked tasks (with reasons)
  - Delegation history
```

## Usage Patterns

### Automatic Activation
```yaml
auto_activation_triggers:
  complexity_threshold: 0.7
  file_count_threshold: 20
  domain_count_threshold: 2
  explicit_keywords:
    - "comprehensive"
    - "systematically"
    - "thoroughly"
```

### Manual Override
```bash
# Force orchestration mode
ultrawork <task>

# Specific specialist
deepwork <architecture question>  # → Oracle
quickfix <bug>                     # → Analyzer
research <topic>                   # → Librarian
```

## Best Practices

### 1. Task Decomposition
- Break large tasks into specialist-sized chunks
- Identify parallel opportunities early
- Define clear completion criteria

### 2. Specialist Utilization
- Match specialists to their expertise
- Don't override specialist recommendations
- Trust verification steps

### 3. Context Preservation
- Save state before compaction
- Document delegation decisions
- Track cross-agent dependencies

### 4. Quality Assurance
- Verify each specialist's output
- Cross-check between specialists
- Validate against original requirements

## External AI Platform Integration

### Multi-AI Orchestration (NEW)

See `MULTI-AI-ORCHESTRATION.md` for complete cross-platform AI coordination details.

```yaml
external_agents:
  gemini_cli:
    role: "Large context analysis specialist"
    context_window: "1M+ tokens"
    activation:
      - context_size > 200000 tokens
      - task_type: "large_codebase_analysis"
      - task_type: "visual_analysis"
      - task_type: "comprehensive_research"
    integration:
      - Slash command: /gemini
      - Direct bash: gemini -p "<prompt>" -f <files>

  codex_cli:
    role: "Rapid prototyping specialist"
    activation:
      - task_type: "rapid_prototyping"
      - task_type: "boilerplate_generation"
      - task_type: "framework_scaffolding"
    integration:
      - Slash command: /codex-proto
      - Direct bash: codex "<prompt>"

routing_matrix:
  large_analysis: gemini
  rapid_prototyping: codex
  complex_reasoning: claude
  code_review: claude
  visual_analysis: gemini
  architecture_decisions: claude
  boilerplate: codex
```

### Dual-Agent Loop Pattern

```yaml
dual_agent_loop:
  detector: gemini  # Scans for issues
  fixer: claude     # Resolves issues

  workflow:
    1: "Gemini scans codebase, appends issues to todo.md"
    2: "Claude fixes first unchecked issue"
    3: "Repeat until todo.md is empty"

  coordination:
    shared_file: ".claude/todo.md"
    max_iterations: 20
    rate_limit: "5s between cycles"
```

## Spec-Driven Pre-Implementation (NEW)

See `SPEC-ATOMIZATION.md` for complete pre-implementation workflow details.

### Mandatory Spec Phase

```yaml
spec_requirement:
  trigger: "Before ANY implementation work"

  phases:
    1_requirements:
      output: "requirements.md"
      content: ["explicit_requirements", "implicit_requirements", "success_criteria"]

    2_design:
      output: "design.md"
      content: ["architecture_impact", "risks", "strategy"]

    3_tasks:
      output: "tasks.md"
      content: ["atomic_tasks", "dependencies", "complexity_scores"]

    4_approval:
      gate: "Human review required"
      criteria: ["scope_validated", "approach_confirmed"]
```

### Atomization Rules

```yaml
atomic_task_criteria:
  max_files_affected: 3
  max_duration: "30 minutes"
  testable_in_isolation: true
  clear_completion_criteria: true
  single_responsibility: true
```

## Evolution Feedback Loop (NEW)

### Outcome-Based Learning

```yaml
feedback_loop:
  capture_phase:
    timing: "After each task/session completion"
    data_points:
      - planned_vs_actual_duration
      - estimated_vs_actual_complexity
      - predicted_vs_actual_files_changed
      - agent_routing_decisions
      - handoff_success_rate
      - spec_accuracy_score

  analyze_phase:
    frequency: "Per session retrospective"
    analysis:
      - Pattern recognition in successful workflows
      - Bottleneck identification
      - Cost-efficiency analysis
      - Agent utilization optimization

  apply_phase:
    actions:
      - Update routing matrix weights
      - Refine handoff templates
      - Optimize agent selection criteria
      - Improve spec templates
      - Adjust complexity estimation

  validate_phase:
    method: "A/B testing on new tasks"
    metrics:
      - Improvement in task completion rate
      - Reduction in rework cycles
      - Better spec accuracy
    rollback: "If degradation > 10%, revert changes"
```

### Continuous Improvement Metrics

```yaml
improvement_metrics:
  routing_accuracy:
    definition: "Correct agent selected for task type"
    target: "> 85%"
    measurement: "Successful task completion rate per agent"

  handoff_success:
    definition: "Clean context transfer between agents/sessions"
    target: "> 95%"
    measurement: "Tasks continued without re-explanation"

  spec_accuracy:
    definition: "Predicted vs actual implementation metrics"
    target: "> 80%"
    measurement: "Task count, file count, duration accuracy"

  evolution_rate:
    definition: "Improvement in metrics over time"
    target: "> 5% per month"
    measurement: "Rolling average of all metrics"
```

### Knowledge Persistence

```yaml
knowledge_persistence:
  session_state:
    file: ".claude/knowledge/session-state.json"
    content:
      - Active tasks and status
      - Agent delegation history
      - Routing decisions made
      - Learnings captured

  project_memory:
    file: ".claude/knowledge/project-memory.md"
    content:
      - Successful patterns discovered
      - Common pitfalls identified
      - Optimal agent routing for this project
      - Spec accuracy baselines

  evolution_log:
    file: ".claude/knowledge/evolution-log.md"
    content:
      - Template updates made
      - Routing matrix changes
      - Improvement metrics over time
      - A/B test results
```

## Zero-Downtime Workflow Verification

### Continuous Operation Checklist

```yaml
zero_downtime_verification:
  session_continuity:
    - [ ] HANDOFF.md properly maintained
    - [ ] State preserved between sessions
    - [ ] No context drift detected
    - [ ] Clean baton passing protocol

  multi_agent_coordination:
    - [ ] Shared context layer functional
    - [ ] Agent handoffs successful
    - [ ] Parallel execution working
    - [ ] Result aggregation complete

  evolution_capability:
    - [ ] Feedback loop operational
    - [ ] Metrics being captured
    - [ ] Templates improving over time
    - [ ] Knowledge base growing

  spec_integration:
    - [ ] Pre-implementation specs created
    - [ ] Atomization working correctly
    - [ ] Validation gates functional
    - [ ] Retrospectives generating insights
```

### Health Check Command

```bash
# Verify system integrity
/health-check

# Output:
# - Session state: OK/WARNING/ERROR
# - Agent routing: OK/WARNING/ERROR
# - Evolution loop: OK/WARNING/ERROR
# - Spec pipeline: OK/WARNING/ERROR
# - HANDOFF integrity: OK/WARNING/ERROR
```
