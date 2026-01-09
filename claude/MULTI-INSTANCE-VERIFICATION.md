# MULTI-INSTANCE-VERIFICATION.md - Independent Claude Review Pattern

> "Fresh eyes catch what familiar eyes miss. Independent verification beats self-review."
>
> — Inspired by Anthropic's Multi-Claude Workflows

Claude Code를 독립적인 여러 인스턴스로 실행하여 상호 검증하는 패턴입니다.

## Core Philosophy

```yaml
principles:
  independent_context: "각 인스턴스는 독립적인 컨텍스트 유지"
  unbiased_review: "구현 과정을 모르는 상태에서 검증"
  writer_reviewer_separation: "작성자와 검토자 역할 분리"
  fresh_perspective: "새로운 시각으로 문제 발견"
```

## Pattern Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  MULTI-INSTANCE VERIFICATION PATTERN                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Terminal Tab 1          Terminal Tab 2           Terminal Tab 3       │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐        │
│  │   WRITER    │         │  REVIEWER   │         │ INTEGRATOR  │        │
│  │  (Instance 1)│        │  (Instance 2)│        │  (Instance 3)│        │
│  │             │         │             │         │             │        │
│  │ Implement   │────────►│ Review      │────────►│ Integrate   │        │
│  │ Feature     │         │ (Fresh Eyes)│         │ Feedback    │        │
│  │             │         │             │         │             │        │
│  └─────────────┘         └─────────────┘         └─────────────┘        │
│        │                       │                       │                │
│        │                       │                       │                │
│        ▼                       ▼                       ▼                │
│   code_changes          review_findings         final_code             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Use Cases

### 1. Critical Code Changes
**시나리오**: 보안, 성능, 아키텍처에 중요한 변경

**이점**:
- 구현자가 놓친 보안 취약점 발견
- 성능 병목 조기 식별
- 아키텍처 일관성 검증

### 2. Complex Refactoring
**시나리오**: 대규모 리팩토링, 레거시 마이그레이션

**이점**:
- 회귀 버그 조기 발견
- 엣지 케이스 누락 방지
- 테스트 커버리지 개선

### 3. API Design Review
**시나리오**: 외부 API, 라이브러리 인터페이스 설계

**이점**:
- 사용성 문제 조기 발견
- 일관성 검증
- 문서화 품질 향상

## Implementation Patterns

### Pattern 1: Sequential Review (순차 검증)

```bash
# Terminal Tab 1: Implementation
cd /path/to/project
claude

> "Implement OAuth2 authentication with PKCE flow:
   1. Add /auth/login endpoint
   2. Implement PKCE challenge/verifier
   3. Add token refresh logic
   4. Write integration tests"

# [Claude implements the feature]
# [Exit when complete]

# Terminal Tab 2: Fresh Review (after Tab 1 completes)
cd /path/to/project
claude

> "You are a security-focused code reviewer. Review the OAuth2 implementation
   in the auth/ directory. You haven't seen the implementation process.

   Focus on:
   - Security vulnerabilities (PKCE implementation correctness)
   - Token storage and expiration handling
   - Error handling and edge cases
   - Test coverage gaps

   Provide specific, actionable feedback with file:line references."

# Terminal Tab 3: Integration (after Tab 2 completes)
cd /path/to/project
claude

> "The OAuth2 implementation has been reviewed. Here are the findings:
   [paste review findings]

   Address each issue systematically. Verify with tests after each fix."
```

**Benefits**:
- ✅ Unbiased review (no implementation context)
- ✅ Specific, actionable feedback
- ✅ Systematic issue resolution
- ❌ Slower (sequential execution)

---

### Pattern 2: Parallel Execution (병렬 실행)

```bash
# Terminal Tab 1: Feature A
cd /path/to/project
claude
> "Implement user registration flow"

# Terminal Tab 2: Feature B (parallel)
cd /path/to/project
claude
> "Implement password reset flow"

# Terminal Tab 3: Cross-Review (after both complete)
cd /path/to/project
claude
> "Review the integration between registration and password reset.
   Check for:
   - Shared code duplication
   - Inconsistent error handling
   - Missing edge case coverage"
```

**Benefits**:
- ✅ Faster (parallel execution)
- ✅ Integration consistency check
- ❌ Requires independent features

---

### Pattern 3: Git Worktrees (경량 병렬)

```bash
# Setup: Create multiple worktrees
git worktree add ../project-implement main
git worktree add ../project-review main
git worktree add ../project-integrate main

# Terminal Tab 1: Implementation Worktree
cd ../project-implement
git checkout -b feature/oauth-implementation
claude
> "Implement OAuth2 with PKCE"

# Terminal Tab 2: Review Worktree (independent filesystem)
cd ../project-review
git checkout feature/oauth-implementation  # after Tab 1 commits
claude
> "Fresh review of OAuth2 implementation"

# Terminal Tab 3: Integration Worktree
cd ../project-integrate
git checkout feature/oauth-implementation  # after Tab 2
claude
> "Integrate review feedback"

# Cleanup
git worktree remove ../project-implement
git worktree remove ../project-review
git worktree remove ../project-integrate
```

**Benefits**:
- ✅ Isolated file systems (no conflict)
- ✅ Independent git histories
- ✅ Lightweight (same .git/)
- ✅ Easy cleanup

**Best Practices**:
1. Use consistent naming: `../project-{role}`
2. One terminal tab per worktree
3. Clean up when finished: `git worktree remove`
4. Check worktree list: `git worktree list`

---

### Pattern 4: /clear Command (단일 인스턴스)

```bash
# Single terminal, multiple contexts
claude

# Phase 1: Implementation
> "Implement feature X"
[Implementation complete]

# Phase 2: Reset context
/clear

# Phase 3: Fresh review
> "Review the implementation of feature X in [directory].
   You haven't seen how it was implemented.
   Provide objective, unbiased feedback."

# Phase 4: Reset again
/clear

# Phase 5: Integration
> "Here's the review feedback: [paste]
   Address each issue."
```

**Benefits**:
- ✅ Single terminal (simpler)
- ✅ Context isolation via /clear
- ❌ Less separation than multiple instances
- ❌ Requires manual /clear discipline

---

## Verification Checklist

### For Writer (Instance 1)
```yaml
before_submission:
  - [ ] Code implements all requirements
  - [ ] Tests pass locally
  - [ ] Lint/typecheck clean
  - [ ] No console.log or debug code
  - [ ] Git commit with clear message

documentation:
  - [ ] Add comments for complex logic
  - [ ] Update relevant documentation
  - [ ] Include examples if public API
```

### For Reviewer (Instance 2)
```yaml
review_focus:
  security:
    - [ ] Input validation
    - [ ] SQL injection prevention
    - [ ] XSS prevention
    - [ ] Authentication/authorization
    - [ ] Secrets not hardcoded

  quality:
    - [ ] Code readability
    - [ ] Error handling
    - [ ] Edge cases covered
    - [ ] Performance implications

  testing:
    - [ ] Test coverage adequate
    - [ ] Tests actually test logic
    - [ ] Edge cases tested

  architecture:
    - [ ] Consistent with existing patterns
    - [ ] No unnecessary complexity
    - [ ] Proper separation of concerns
```

### For Integrator (Instance 3)
```yaml
integration_tasks:
  - [ ] Address all critical issues
  - [ ] Address high-priority issues
  - [ ] Document deferred issues (if any)
  - [ ] Re-run tests after fixes
  - [ ] Verify lint/typecheck still pass
  - [ ] Final commit with "Addressed review feedback"
```

---

## Automation & Tooling

### Helper Script: `multi-claude-verify.sh`

```bash
#!/bin/bash
# Helper for multi-instance verification workflow

set -e

FEATURE_NAME="$1"
BRANCH_NAME="feature/${FEATURE_NAME}"

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: $0 <feature-name>"
    exit 1
fi

echo "🚀 Starting multi-instance verification for: $FEATURE_NAME"

# Step 1: Create worktrees
echo "📁 Creating worktrees..."
git worktree add ../project-implement-${FEATURE_NAME} main
git worktree add ../project-review-${FEATURE_NAME} main
git worktree add ../project-integrate-${FEATURE_NAME} main

# Step 2: Implementation instructions
echo ""
echo "✅ Worktrees created. Next steps:"
echo ""
echo "Terminal Tab 1 (Implementation):"
echo "  cd ../project-implement-${FEATURE_NAME}"
echo "  git checkout -b ${BRANCH_NAME}"
echo "  claude"
echo "  > [Implement the feature]"
echo ""
echo "Terminal Tab 2 (Review - after Tab 1):"
echo "  cd ../project-review-${FEATURE_NAME}"
echo "  git checkout ${BRANCH_NAME}"
echo "  claude"
echo "  > [Review the implementation]"
echo ""
echo "Terminal Tab 3 (Integration - after Tab 2):"
echo "  cd ../project-integrate-${FEATURE_NAME}"
echo "  git checkout ${BRANCH_NAME}"
echo "  claude"
echo "  > [Integrate feedback]"
echo ""
echo "When finished:"
echo "  ./multi-claude-cleanup.sh ${FEATURE_NAME}"
```

### Cleanup Script: `multi-claude-cleanup.sh`

```bash
#!/bin/bash
# Cleanup worktrees after multi-instance verification

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: $0 <feature-name>"
    exit 1
fi

echo "🧹 Cleaning up worktrees for: $FEATURE_NAME"

git worktree remove ../project-implement-${FEATURE_NAME} || echo "Already removed: implement"
git worktree remove ../project-review-${FEATURE_NAME} || echo "Already removed: review"
git worktree remove ../project-integrate-${FEATURE_NAME} || echo "Already removed: integrate"

echo "✅ Cleanup complete"
git worktree list
```

---

## Integration with Context Engineering

### Moon Commands Integration

```bash
# New command: /moon-verify-fresh
/moon-verify-fresh "OAuth2 implementation in auth/"
```

**Workflow**:
1. Detect if feature is already implemented
2. If yes: Launch fresh review instance
3. If no: Guide user to implement first
4. Collect review findings
5. Guide integration of feedback

### CLAUDE.md Configuration

Add to project's `claude/CLAUDE.md`:

```markdown
## Multi-Instance Verification

For critical changes, use independent verification:

1. **Implementation** (Tab 1): Implement feature
2. **Review** (Tab 2): Fresh review after `/clear` or new instance
3. **Integration** (Tab 3): Address feedback

**When to use**:
- Security-sensitive code
- Public API changes
- Complex refactoring
- Critical bug fixes
```

---

## Comparison: Single vs Multi-Instance

| Aspect | Single Instance | Multi-Instance |
|--------|-----------------|----------------|
| **Bias** | High (knows implementation) | Low (fresh perspective) |
| **Setup** | Simple (/clear) | Moderate (new terminals) |
| **Isolation** | Context only | Full separation |
| **Speed** | Faster | Slower (sequential) |
| **Quality** | Good | Excellent |
| **Best For** | Quick reviews | Critical code |

---

## Real-World Example

### Scenario: Implementing Payment Integration

```bash
# Terminal 1: Implementation
claude
> "Implement Stripe payment integration:
   1. Add /api/payments/charge endpoint
   2. Implement idempotency with Redis
   3. Add webhook handler for payment.succeeded
   4. Write integration tests with Stripe test keys"

# [Implementation complete, committed]

# Terminal 2: Security Review (fresh instance)
claude
> "You are a payment security expert. Review the Stripe integration
   in api/payments/ without seeing how it was implemented.

   Focus on:
   - PCI DSS compliance (no storing card data)
   - Idempotency implementation correctness
   - Webhook signature verification
   - Error handling for failed payments
   - Test key security

   Provide specific findings with file:line references."

# Example review output:
# ❌ CRITICAL: api/payments/charge.ts:45
#    Stripe API key hardcoded. Use environment variable.
#
# ⚠️  HIGH: api/payments/webhook.ts:23
#    Missing webhook signature verification. Vulnerable to replay attacks.
#
# ⚠️  MEDIUM: api/payments/charge.ts:67
#    Idempotency key not persisted. Could cause double charges on retry.
#
# ✅ PASS: Test coverage adequate (87%)

# Terminal 3: Integration
claude
> "Address the security review findings:
   [paste findings]

   Fix each issue, verify with tests, commit individually."
```

**Result**: 3 critical/high security issues caught before production.

---

## Best Practices

### Do ✅
- Use multi-instance for critical code
- Give reviewer specific focus areas
- Commit after each phase for traceability
- Use git worktrees for true isolation
- Document review findings in commit messages

### Don't ❌
- Don't skip verification for "simple" changes (they often aren't)
- Don't let the same instance self-review without /clear
- Don't ignore medium/low findings (they accumulate)
- Don't forget to cleanup worktrees

---

## Troubleshooting

### Issue: "Reviewer has too much context"
**Solution**: Use `/clear` before review or spawn completely new terminal.

### Issue: "Git conflicts between worktrees"
**Solution**: Each worktree should use different branches or sequential workflow.

### Issue: "Too slow for simple changes"
**Solution**: Reserve multi-instance for high-stakes code. Use single-instance /clear for routine work.

### Issue: "Review findings are too vague"
**Solution**: Give reviewer specific focus areas and ask for file:line references.

---

## References

- [Anthropic Best Practices: Multi-Claude Workflows](https://www.anthropic.com/engineering/claude-code-best-practices) ⭐⭐⭐⭐⭐
- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)
- Context Engineering: MULTI-AI-ORCHESTRATION.md

---

*Generated by Context Engineering Framework*
*Pattern Source: Anthropic Official Best Practices*
