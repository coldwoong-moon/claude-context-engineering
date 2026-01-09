# Native vs Custom Feature Analysis

> Claude Code 네이티브 기능과 커스텀 구현의 구분

## Summary

**현재 문제**:
- ~/.claude/ 문서: 2,150줄의 컨텍스트 오버헤드
- 네이티브 기능 문서화: 불필요한 중복
- 실제 커스텀 가치: 분산되어 있음

**목표**:
- 컨텍스트 오버헤드: 2,150줄 → 500줄 이하 (75% 감소)
- 네이티브 기능: 문서화 대신 직접 활용
- 커스텀 가치: 명확한 분리 및 집중

---

## Native Features (No Documentation Needed)

Claude Code에서 네이티브로 지원하며, 별도 문서화가 불필요한 기능들:

### 1. Hook System (9 Events)
```yaml
native_hooks:
  - PreToolUse      # 도구 실행 전
  - PostToolUse     # 도구 실행 후
  - PermissionRequest
  - UserPromptSubmit
  - Stop
  - SubagentStop
  - SessionStart
  - SessionEnd
  - PreCompact
  - Notification
```
**→ 문서화 불필요, 구현만 필요**

### 2. Subagent System
```yaml
native_subagents:
  built_in:
    - Explore     # Haiku, read-only
    - Plan        # Plan mode
    - General     # Multi-step tasks
  custom_config:
    - name, description, model
    - tools, permissionMode
    - hooks, skills
```
**→ YAML 프론트매터만 필요, 시스템 설명 불필요**

### 3. Skill System
```yaml
native_skills:
  auto_detection: "description 기반 자동 감지"
  invocation: "/skill-name 또는 Skill tool"
  config: "allowed-tools, model, context"
```
**→ 네이티브 작동, 문서화 불필요**

### 4. MCP Integration
```yaml
native_mcp:
  installation: "claude mcp add"
  scopes: "local, project, user"
  capabilities: "tools, resources, prompts"
```
**→ CLI로 관리, MCP.md 불필요**

### 5. Permission System
```yaml
native_permissions:
  config: "settings.json에서 allow/deny/ask"
  patterns: "glob, regex 지원"
  modes: "default, acceptEdits, dontAsk, bypassPermissions"
```
**→ 설정 파일만 필요, 문서화 불필요**

### 6. Memory System
```yaml
native_memory:
  hierarchy:
    - CLAUDE.md (project)
    - .claude/rules/*.md (conditional)
    - ~/.claude/CLAUDE.md (user)
  features:
    - "@" imports
    - path conditions
```
**→ 네이티브 작동, 시스템 설명 불필요**

### 7. Slash Commands
```yaml
native_commands:
  built_in: "/config, /mcp, /memory, /hooks, /plan, /compact, /cost..."
  custom: ".claude/commands/*.md"
```
**→ 마크다운 작성만 필요**

### 8. Output Styles
```yaml
native_output_styles:
  location: ".claude/output-styles/*.md"
  invocation: "/output-style"
```
**→ 네이티브 작동**

---

## Custom Implementations (Documentation + Code Needed)

실제로 커스텀 구현이 필요한 영역:

### 1. Workflow Patterns
```yaml
custom_workflows:
  ralph_loop:
    purpose: "완료까지 작업 지속"
    implementation: "Stop hook + prompt-based decision"
    file: "hooks/ralph-loop.py"

  verification_loop:
    purpose: "서브에이전트 결과 검증"
    implementation: "SubagentStop hook"
    file: "hooks/verification-loop.py"

  spec_atomization:
    purpose: "Pre-implementation 스펙 세분화"
    implementation: "Custom workflow in CLAUDE.md"
    status: "문서 + skill 필요"

  multi_ai_orchestration:
    purpose: "Gemini/Codex 연동"
    implementation: "Bash integration via commands"
    status: "command + hook 필요"
```

### 2. Domain Personas
```yaml
custom_personas:
  value_add: "네이티브 subagent보다 상세한 도메인 전문성"
  needed:
    - oracle.md        # Deep reasoning specialist
    - librarian.md     # Evidence-based research
    - (selected others with unique value)
  redundant:
    - 네이티브 Explore와 중복되는 에이전트
    - 단순 tool 조합만 다른 에이전트
```

### 3. Evolution Feedback Loop
```yaml
custom_evolution:
  purpose: "자기 진화 시스템"
  implementation:
    - metrics collection hook
    - retrospective automation
    - template improvement
  status: "구현 필요"
```

### 4. Quality Gates
```yaml
custom_quality:
  purpose: "8단계 검증 사이클"
  implementation:
    - PostToolUse hooks
    - Validation scripts
  status: "일부 구현됨"
```

---

## Redundancy Analysis

### Files to REMOVE/CONSOLIDATE

| File | Lines | Reason | Action |
|------|-------|--------|--------|
| `MCP.md` | 225 | Native MCP docs exist | REMOVE |
| `FLAGS.md` | 220 | Can use native settings | CONSOLIDATE to CLAUDE.md |
| `MODES.md` | 309 | Mostly native features | EXTRACT only custom parts |
| `COMMANDS.md` | 159 | Native command system | REMOVE, use actual commands |
| `ORCHESTRATOR.md` | 533 | Overlaps native Task tool | CONSOLIDATE essentials |

**예상 절감: ~1,446줄 (67%)**

### Files to KEEP (with optimization)

| File | Lines | Value | Action |
|------|-------|-------|--------|
| `PRINCIPLES.md` | 160 | Core philosophy | KEEP, trim |
| `RULES.md` | 65 | Actionable rules | KEEP |
| `PERSONAS.md` | 467 | Domain expertise | SLIM to 10 essential |

---

## Recommended New Structure

```
~/.claude/
├── CLAUDE.md              # 최소화된 진입점 (<100줄)
│   └── @rules.md          # 핵심 규칙만
│
├── agents/                # 필수 에이전트만 (5-7개)
│   ├── oracle.md          # Deep reasoning
│   ├── librarian.md       # Evidence-based
│   └── ...
│
├── commands/              # 커스텀 워크플로우
│   ├── spec.md            # Spec atomization
│   ├── gemini.md          # Gemini delegation
│   └── ...
│
├── hooks/                 # 자동화 구현
│   ├── evolution/         # 피드백 루프
│   │   ├── metrics.py
│   │   └── retrospective.py
│   ├── quality/           # 검증
│   │   ├── validation.py
│   │   └── lint-check.py
│   └── workflow/          # 워크플로우
│       ├── ralph-loop.py
│       └── spec-check.py
│
└── skills/                # 복합 기능
    └── context-engineering/
        └── SKILL.md
```

---

## Implementation Priority

### Phase 1: Cleanup (즉시)
1. ~/.claude/CLAUDE.md 최소화
2. 중복 문서 제거
3. 필수 에이전트만 유지

### Phase 2: Automation (단기)
1. Evolution feedback hook 구현
2. Quality gate hooks 강화
3. Spec atomization command 구현

### Phase 3: Integration (중기)
1. Multi-AI orchestration 완성
2. Self-evolving metrics 시스템
3. A/B testing framework

---

## Token Efficiency Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| CLAUDE.md total | 2,150줄 | 500줄 | 77% 감소 |
| Context overhead | ~8,000 tokens | ~2,000 tokens | 75% 감소 |
| Actual automation | 20% | 80% | 4x 향상 |
| Native feature usage | 30% | 90% | 3x 향상 |
