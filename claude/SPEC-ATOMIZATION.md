# SPEC-ATOMIZATION.md - Pre-Implementation Specification Refinement

> "Spec-Driven Development: Separate design from implementation. Never code before you spec."
>
> "Feature -> User Stories -> Tasks -> Atomic Implementation Units"

작업 이전에 요구사항을 구체화하고, 가장 작은 단위로 원자화시키는 Spec 세분화 전략입니다.

## Core Philosophy

```yaml
principles:
  spec_first: "No implementation without specification"
  decomposition: "Complex -> Simple -> Atomic"
  validation_at_each_level: "Validate before proceeding deeper"
  human_in_loop: "Human review at critical gates"
  evolution_feedback: "Learn from outcomes to improve specs"
```

## Spec-Driven Development Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPEC ATOMIZATION PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   [IDEA]                                                                 │
│      │                                                                   │
│      ▼                                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 1: REQUIREMENTS EXTRACTION            │                       │
│   │  - Analyze user request                      │                       │
│   │  - Extract explicit requirements             │                       │
│   │  - Identify implicit requirements            │                       │
│   │  - Define success criteria                   │                       │
│   │  → Output: requirements.md                   │                       │
│   └──────────────────┬──────────────────────────┘                       │
│                      │                                                   │
│                      ▼                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 2: SOLUTION DESIGN                    │                       │
│   │  - Analyze existing codebase patterns        │                       │
│   │  - Evaluate architecture impact              │                       │
│   │  - Identify risks and dependencies           │                       │
│   │  - Propose implementation strategy           │                       │
│   │  → Output: design.md                         │                       │
│   └──────────────────┬──────────────────────────┘                       │
│                      │                                                   │
│                      ▼                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 3: TASK DECOMPOSITION                 │                       │
│   │  - Break into user stories                   │                       │
│   │  - Decompose to atomic tasks                 │                       │
│   │  - Define dependencies and order             │                       │
│   │  - Assign complexity scores                  │                       │
│   │  → Output: tasks.md                          │                       │
│   └──────────────────┬──────────────────────────┘                       │
│                      │                                                   │
│                      ▼                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 4: VALIDATION GATE                    │                       │
│   │  - Review with user/stakeholder              │                       │
│   │  - Validate scope and approach               │                       │
│   │  - Confirm resource allocation               │                       │
│   │  → Output: approved-spec.md                  │                       │
│   └──────────────────┬──────────────────────────┘                       │
│                      │                                                   │
│                      ▼                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 5: ITERATIVE IMPLEMENTATION           │                       │
│   │  - Execute one task at a time                │                       │
│   │  - Validate after each task                  │                       │
│   │  - Update spec if needed                     │                       │
│   │  - Feed learnings back                       │                       │
│   └──────────────────┬──────────────────────────┘                       │
│                      │                                                   │
│                      ▼                                                   │
│   ┌─────────────────────────────────────────────┐                       │
│   │  Phase 6: RETROSPECTIVE & EVOLUTION          │                       │
│   │  - Compare outcomes vs. spec                 │                       │
│   │  - Document lessons learned                  │                       │
│   │  - Update spec templates                     │                       │
│   │  - Feed into future specs                    │                       │
│   └─────────────────────────────────────────────┘                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Phase 1: Requirements Extraction

### Input Analysis Protocol

```yaml
requirement_extraction:
  explicit_requirements:
    - Direct user statements
    - Specific feature requests
    - Stated constraints

  implicit_requirements:
    - Inferred from context
    - Based on domain knowledge
    - Derived from existing patterns

  anti_requirements:
    - What NOT to do
    - Existing behaviors to preserve
    - Out-of-scope items
```

### Requirements Document Template

```markdown
# Requirements: [Feature Name]

## 1. Overview
**Request**: [Original user request]
**Interpreted Goal**: [Refined understanding]

## 2. Explicit Requirements
- [ ] REQ-001: [Requirement description]
- [ ] REQ-002: [Requirement description]

## 3. Implicit Requirements
- [ ] IMPL-001: [Derived requirement]
- [ ] IMPL-002: [Derived requirement]

## 4. Anti-Requirements (Out of Scope)
- ANTI-001: [What NOT to do]
- ANTI-002: [What NOT to do]

## 5. Success Criteria
| Criterion | Measurement | Target |
|-----------|-------------|--------|
| [Metric]  | [How]       | [Value]|

## 6. Constraints
- Technical: [Constraints]
- Timeline: [Constraints]
- Resources: [Constraints]

## 7. Questions for Clarification
- Q1: [Ambiguous point]
- Q2: [Need more info]
```

## Phase 2: Solution Design

### Design Analysis Workflow

```yaml
design_analysis:
  step_1_codebase_scan:
    action: "Analyze existing patterns and architecture"
    tools: [Read, Grep, Glob]
    output: "pattern_analysis.md"

  step_2_impact_assessment:
    action: "Evaluate changes across codebase"
    dimensions:
      - files_affected
      - modules_impacted
      - dependencies_changed
    output: "impact_matrix"

  step_3_risk_identification:
    action: "Identify potential issues"
    categories:
      - technical_risks
      - integration_risks
      - performance_risks
      - security_risks
    output: "risk_register"

  step_4_strategy_proposal:
    action: "Define implementation approach"
    options:
      - approach_a: "[Description + pros/cons]"
      - approach_b: "[Description + pros/cons]"
    recommendation: "Selected approach with rationale"
```

### Design Document Template

```markdown
# Design: [Feature Name]

## 1. Codebase Analysis

### Existing Patterns
- Pattern 1: [Found in files]
- Pattern 2: [Found in files]

### Relevant Files
| File | Purpose | Impact Level |
|------|---------|--------------|
| path/file.ts | [Purpose] | High/Med/Low |

## 2. Proposed Architecture

### Component Diagram
```
[Visual representation]
```

### Data Flow
[Sequence or flow diagram]

## 3. Implementation Strategy

### Approach
[Detailed approach description]

### Rationale
[Why this approach over alternatives]

## 4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

## 5. Dependencies
- External: [Libraries, APIs]
- Internal: [Modules, functions]
```

## Phase 3: Task Decomposition

### Atomization Rules

```yaml
atomization_principles:
  atomic_task_criteria:
    max_files_affected: 3
    max_duration: "30 minutes"
    testable_in_isolation: true
    clear_completion_criteria: true
    single_responsibility: true

  decomposition_levels:
    level_1_epic: "Large feature or initiative"
    level_2_story: "User-facing functionality"
    level_3_task: "Technical implementation unit"
    level_4_subtask: "Atomic code change"

  dependency_rules:
    - "Prefer parallel tasks over sequential"
    - "Isolate risky changes"
    - "Foundation before features"
```

### Task Decomposition Algorithm

```python
def atomize_requirement(requirement):
    """
    Decompose a requirement into atomic tasks

    Criteria for atomic task:
    - Affects 1-3 files maximum
    - Completable in <30 min
    - Has clear success criteria
    - Independently testable
    """

    # Step 1: Break into user stories
    stories = extract_user_stories(requirement)

    # Step 2: For each story, identify tasks
    tasks = []
    for story in stories:
        story_tasks = decompose_story(story)
        tasks.extend(story_tasks)

    # Step 3: Validate atomicity
    for task in tasks:
        if not is_atomic(task):
            sub_tasks = further_decompose(task)
            tasks.remove(task)
            tasks.extend(sub_tasks)

    # Step 4: Establish dependencies
    task_graph = build_dependency_graph(tasks)

    # Step 5: Assign complexity scores
    for task in tasks:
        task.complexity = calculate_complexity(task)

    return task_graph
```

### Task Document Template

```markdown
# Tasks: [Feature Name]

## Epic Overview
**Goal**: [High-level objective]
**Total Complexity**: [Sum of task complexities]
**Estimated Duration**: [Total estimate]

---

## User Story 1: [Story Name]
**As a** [user type]
**I want to** [action]
**So that** [benefit]

### Task 1.1: [Task Name]
- **ID**: TASK-001
- **Complexity**: 1-5 (Fibonacci: 1, 2, 3, 5, 8)
- **Files**: `path/to/file.ts`
- **Dependencies**: None | TASK-XXX
- **Completion Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Test Plan**: [How to verify]

### Task 1.2: [Task Name]
...

---

## Dependency Graph

```
TASK-001 ─┬─► TASK-002 ──► TASK-004
          │
          └─► TASK-003 ──► TASK-005
```

## Execution Order
1. [TASK-001] - Foundation
2. [TASK-002, TASK-003] - Parallel
3. [TASK-004, TASK-005] - Parallel
```

## Phase 4: Validation Gate

### Gate Criteria

```yaml
validation_gates:
  requirements_gate:
    - All explicit requirements documented
    - Success criteria measurable
    - Constraints clearly stated
    - Stakeholder approval obtained

  design_gate:
    - Architecture impact assessed
    - Risks identified and mitigated
    - Approach validated against patterns
    - Technical review passed

  tasks_gate:
    - All tasks are atomic
    - Dependencies mapped
    - Complexity scored
    - Test plan defined

  pre_implementation_gate:
    - All above gates passed
    - Resources allocated
    - Timeline confirmed
    - Rollback plan ready
```

### Approval Workflow

```yaml
approval_process:
  auto_approve:
    conditions:
      - complexity < 5
      - files_affected < 3
      - no_breaking_changes
      - existing_pattern_followed

  require_review:
    conditions:
      - complexity >= 5
      - architecture_impact
      - new_patterns_introduced
      - external_dependencies

  require_explicit_approval:
    conditions:
      - production_impact
      - security_changes
      - data_migration
      - breaking_changes
```

## Phase 5: Iterative Implementation

### Execution Protocol

```yaml
implementation_protocol:
  per_task:
    1_load_context:
      - Read task specification
      - Load relevant files
      - Understand dependencies

    2_implement:
      - Make atomic changes
      - Follow existing patterns
      - Write tests alongside

    3_validate:
      - Run tests
      - Check lint
      - Verify criteria met

    4_checkpoint:
      - Update HANDOFF.md
      - Mark task complete
      - Note any blockers

    5_commit:
      - Atomic commit per task
      - Clear commit message
      - Reference task ID
```

### Progress Tracking

```markdown
# Implementation Progress: [Feature Name]

## Current Status
- **Phase**: Implementation
- **Active Task**: TASK-003
- **Progress**: 60% (6/10 tasks)

## Completed Tasks
| Task | Duration | Notes |
|------|----------|-------|
| TASK-001 | 15m | Completed as planned |
| TASK-002 | 25m | Minor adjustment needed |

## In Progress
- **TASK-003**: 70% complete
  - Blocker: [If any]

## Remaining
- TASK-004: Waiting for TASK-003
- TASK-005: Ready to start

## Learnings
- [Insight from implementation]
```

## Phase 6: Retrospective & Evolution

### Outcome Evaluation

```yaml
retrospective_analysis:
  metrics_comparison:
    - planned_duration vs actual_duration
    - estimated_complexity vs actual_complexity
    - predicted_files vs actual_files_changed

  quality_assessment:
    - requirements_met: percentage
    - tests_passing: percentage
    - lint_clean: boolean
    - performance_impact: measurement

  process_evaluation:
    - spec_accuracy: "How well did spec predict reality?"
    - atomization_quality: "Were tasks truly atomic?"
    - dependency_accuracy: "Were dependencies correct?"
```

### Evolution Feedback Loop

```yaml
evolution_loop:
  capture_learnings:
    - Document what worked
    - Document what didn't
    - Identify pattern improvements

  update_templates:
    - Refine requirement templates
    - Improve task decomposition rules
    - Update complexity estimation

  knowledge_base_update:
    - Add to project knowledge
    - Update estimation baselines
    - Record new patterns

  next_iteration_prep:
    - Apply learnings to future specs
    - Adjust validation gates
    - Improve atomization algorithm
```

### Retrospective Document Template

```markdown
# Retrospective: [Feature Name]

## Summary
- **Planned Duration**: X hours
- **Actual Duration**: Y hours
- **Variance**: +/- Z%

## What Went Well
1. [Success point]
2. [Success point]

## What Could Improve
1. [Improvement area]
2. [Improvement area]

## Spec Accuracy Analysis
| Aspect | Predicted | Actual | Accuracy |
|--------|-----------|--------|----------|
| Tasks | 10 | 12 | 83% |
| Files | 5 | 7 | 71% |
| Duration | 3h | 4h | 75% |

## Learnings for Future Specs
1. [Learning to apply]
2. [Learning to apply]

## Template Updates
- [ ] Update requirement template: [Change]
- [ ] Update task decomposition: [Change]
```

## Integration with SuperClaude

### Command Integration

```yaml
spec_commands:
  /spec:
    trigger: "New feature or significant change"
    workflow: "Full spec pipeline"
    output: "requirements.md, design.md, tasks.md"

  /spec-lite:
    trigger: "Small, well-understood changes"
    workflow: "Quick decomposition"
    output: "tasks.md only"

  /spec-review:
    trigger: "Review existing spec"
    workflow: "Validation and refinement"
    output: "Updated spec documents"
```

### Magic Keywords

```yaml
spec_keywords:
  - "spec: <request>" → Full spec workflow
  - "스펙: <request>" → Full spec workflow
  - "atomize: <task>" → Task decomposition only
  - "원자화: <task>" → Task decomposition only
```

### Hook Integration

```yaml
hooks:
  PreImplementation:
    - spec-check.py  # Verify spec exists and is approved

  PostTask:
    - progress-update.py  # Update implementation progress

  PostImplementation:
    - retrospective-trigger.py  # Prompt for retrospective
```

## Best Practices

### 1. Never Skip Spec Phase
- Even "quick fixes" benefit from brief specification
- Use /spec-lite for small changes
- Document reasoning for future reference

### 2. Validate Early and Often
- Don't wait until implementation to discover issues
- Review specs with stakeholders before coding
- Catch scope creep at spec level

### 3. Keep Tasks Truly Atomic
- If you need to explain context, task is too big
- Each task should be independently verifiable
- Prefer more small tasks over fewer large ones

### 4. Embrace Evolution
- Specs will change during implementation
- That's okay - update them as you learn
- Retrospectives improve future specs

### 5. Use Multi-AI Orchestration
- Claude for reasoning and planning
- Gemini for analysis (1M token context)
- Codex for rapid prototyping
- Combine strengths in spec phase

## References

- [JetBrains Spec-Driven Approach](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/)
- [Thoughtworks Spec-Driven Development](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
- [Zencoder AI Engineering Cycle](https://zencoder.ai/blog/idea-spec-workflow-production-the-modern-ai-engineering-cycle)
