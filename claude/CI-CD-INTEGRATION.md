# CI-CD-INTEGRATION.md - Claude Code Headless Automation Guide

> "Automate everything that can be automated. Let CI/CD handle the repetitive, Claude handle the intelligent."
>
> — Based on Anthropic's Headless Automation Best Practices

Claude Code를 CI/CD 파이프라인에 통합하여 자동화된 코드 품질 관리를 구현하는 가이드입니다.

## Core Philosophy

```yaml
principles:
  headless_execution: "Non-interactive mode for automation"
  structured_output: "JSON for programmatic consumption"
  safety_first: "Allowlist-only tool permissions"
  idempotent: "Same input → same output"
  fail_fast: "Errors stop the pipeline"
```

## Headless Mode Basics

### `-p` Flag (Prompt)

```bash
# Basic headless execution
claude -p "Check for console.log statements and remove them"

# With tool permissions
claude -p "Fix lint errors" --allowedTools Edit Bash(npm run lint)

# With JSON output
claude -p "Analyze security issues" --json > analysis.json
```

### Tool Permission Patterns

```yaml
safe_patterns:
  read_only:
    - "Read"
    - "Grep"
    - "Glob"
    - "Bash(git status)"
    - "Bash(npm run lint)"

  write_allowed:
    - "Edit"
    - "Write"
    - "Bash(git add:*)"
    - "Bash(git commit:*)"

  restricted:
    - "Bash(*)"  # Too permissive - use specific patterns
    - "Bash(rm:*)"  # Dangerous
    - "Bash(git push:*)"  # Requires explicit approval
```

---

## Git Hooks Integration

### Pre-Commit Hook

**Purpose**: Automatic code quality checks before each commit.

```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "🤖 Claude Code: Pre-commit checks..."

# 1. Remove console.log statements
claude -p "Remove all console.log statements from staged files. Preserve intentional logging (logger.info, etc.)" \
  --allowedTools Edit Bash(git add:*) \
  --json > /tmp/claude-console-check.json

# Check if changes were made
if jq -e '.changes_made == true' /tmp/claude-console-check.json >/dev/null; then
  echo "✅ Removed console.log statements"
  git add -u
fi

# 2. Fix common linting errors
claude -p "Fix auto-fixable ESLint errors in staged files" \
  --allowedTools Edit Bash(npm run lint -- --fix) Bash(git add:*) \
  --json > /tmp/claude-lint-fix.json

if jq -e '.fixes_applied == true' /tmp/claude-lint-fix.json >/dev/null; then
  echo "✅ Fixed lint errors"
  git add -u
fi

# 3. Final validation
npm run lint
npm run typecheck

echo "✅ Pre-commit checks passed"
```

**Installation**:
```bash
chmod +x .git/hooks/pre-commit
```

---

### Pre-Push Hook

**Purpose**: Validate tests and security before pushing.

```bash
#!/bin/bash
# .git/hooks/pre-push

set -e

echo "🤖 Claude Code: Pre-push validation..."

# 1. Run tests
npm test

# 2. Security scan
claude -p "Scan for common security vulnerabilities (SQL injection, XSS, hardcoded secrets)" \
  --allowedTools Read Grep \
  --json > /tmp/claude-security-scan.json

# Check for critical issues
CRITICAL_COUNT=$(jq '.critical_count // 0' /tmp/claude-security-scan.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "❌ Critical security issues found: $CRITICAL_COUNT"
  jq '.findings[]' /tmp/claude-security-scan.json
  exit 1
fi

echo "✅ Pre-push validation passed"
```

---

### Commit-Msg Hook

**Purpose**: Enforce conventional commit message format.

```bash
#!/bin/bash
# .git/hooks/commit-msg

COMMIT_MSG_FILE=$1

# Read the commit message
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Use Claude to validate and improve
claude -p "Validate this commit message follows Conventional Commits format.
If invalid, suggest improvements:

$COMMIT_MSG

Output JSON:
{
  \"valid\": true/false,
  \"suggestion\": \"improved message (if invalid)\"
}" \
  --json > /tmp/claude-commit-msg.json

IS_VALID=$(jq -r '.valid' /tmp/claude-commit-msg.json)

if [ "$IS_VALID" = "false" ]; then
  SUGGESTION=$(jq -r '.suggestion' /tmp/claude-commit-msg.json)
  echo "❌ Invalid commit message format"
  echo "💡 Suggestion: $SUGGESTION"
  exit 1
fi

echo "✅ Commit message validated"
```

---

## GitHub Actions Integration

### Workflow 1: Claude Code Review on PR

```yaml
# .github/workflows/claude-review.yml

name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  claude-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git diff

      - name: Install Claude Code
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Claude Security Review
        id: security-review
        run: |
          claude -p "Review the PR changes for security issues.
          Focus on:
          - SQL injection vulnerabilities
          - XSS vulnerabilities
          - Authentication/authorization flaws
          - Hardcoded secrets

          Analyze: $(git diff origin/${{ github.base_ref }}...HEAD)

          Output JSON with:
          {
            \"issues\": [{\"severity\": \"critical|high|medium|low\", \"file\": \"path\", \"line\": 123, \"description\": \"...\"}],
            \"summary\": \"Overall assessment\"
          }" \
            --allowedTools Read Grep \
            --json > review.json

          echo "REVIEW_JSON=$(cat review.json | jq -c .)" >> $GITHUB_OUTPUT

      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const review = JSON.parse('${{ steps.security-review.outputs.REVIEW_JSON }}');

            let comment = '## 🤖 Claude Security Review\n\n';
            comment += `**Summary**: ${review.summary}\n\n`;

            if (review.issues.length > 0) {
              comment += '### Issues Found\n\n';
              review.issues.forEach(issue => {
                const emoji = {
                  'critical': '🔴',
                  'high': '🟠',
                  'medium': '🟡',
                  'low': '🟢'
                }[issue.severity];

                comment += `${emoji} **${issue.severity.toUpperCase()}**: \`${issue.file}:${issue.line}\`\n`;
                comment += `${issue.description}\n\n`;
              });
            } else {
              comment += '✅ No security issues found.\n';
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail on Critical Issues
        run: |
          CRITICAL_COUNT=$(jq '[.issues[] | select(.severity == "critical")] | length' review.json)
          if [ "$CRITICAL_COUNT" -gt 0 ]; then
            echo "❌ Found $CRITICAL_COUNT critical security issues"
            exit 1
          fi
```

---

### Workflow 2: Automated Issue Triage

```yaml
# .github/workflows/issue-triage.yml

name: Issue Triage
on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write

    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Classify Issue
        id: classify
        env:
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
        run: |
          claude -p "Classify this GitHub issue:

          Title: $ISSUE_TITLE
          Body: $ISSUE_BODY

          Output JSON:
          {
            \"type\": \"bug|feature|question|documentation|invalid\",
            \"priority\": \"critical|high|medium|low\",
            \"labels\": [\"label1\", \"label2\"],
            \"reasoning\": \"Why this classification\"
          }" \
            --json > classification.json

          echo "CLASSIFICATION=$(cat classification.json | jq -c .)" >> $GITHUB_OUTPUT

      - name: Apply Labels
        uses: actions/github-script@v7
        with:
          script: |
            const classification = JSON.parse('${{ steps.classify.outputs.CLASSIFICATION }}');

            // Add labels
            await github.rest.issues.addLabels({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: classification.labels
            });

            // Add classification comment
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `🤖 **Automated Triage**\n\n**Type**: ${classification.type}\n**Priority**: ${classification.priority}\n\n**Reasoning**: ${classification.reasoning}`
            });
```

---

### Workflow 3: Dependency Update with Claude

```yaml
# .github/workflows/dependency-update.yml

name: Dependency Update
on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday
  workflow_dispatch:

jobs:
  update-deps:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Update Dependencies
        run: |
          claude -p "Check for outdated dependencies and update them one by one.
          For each update:
          1. Run 'npm outdated' to identify updates
          2. Update one dependency
          3. Run tests: npm test
          4. If tests pass, commit with message: 'chore(deps): update [package] to [version]'
          5. If tests fail, revert and document issue
          6. Repeat for next dependency

          Stop after 10 updates or if no more updates available." \
            --allowedTools Edit Bash(npm:*) Bash(git:*) \
            --json > update-log.json

      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore(deps): automated dependency updates"
          title: "🤖 Automated Dependency Updates"
          body: |
            ## Automated Dependency Updates

            Claude Code has updated dependencies with the following process:
            1. Checked for outdated packages
            2. Updated one dependency at a time
            3. Verified tests pass after each update
            4. Committed successful updates

            See commit history for detailed changes.
          branch: deps/automated-update
```

---

## GitLab CI Integration

### `.gitlab-ci.yml` Example

```yaml
stages:
  - lint
  - test
  - security
  - deploy

# Install Claude Code template
.claude_template:
  before_script:
    - curl -fsSL https://claude.ai/install.sh | bash
    - export PATH="$HOME/.local/bin:$PATH"

# Lint with Claude
claude_lint:
  extends: .claude_template
  stage: lint
  script:
    - |
      claude -p "Fix all auto-fixable lint errors" \
        --allowedTools Edit Bash(npm run lint -- --fix) \
        --json > lint-results.json
    - npm run lint  # Verify
  artifacts:
    reports:
      codequality: lint-results.json
    when: always

# Security scan
claude_security:
  extends: .claude_template
  stage: security
  script:
    - |
      claude -p "Perform comprehensive security scan.
      Check for:
      - Hardcoded secrets (API keys, passwords)
      - SQL injection vulnerabilities
      - XSS vulnerabilities
      - Insecure dependencies

      Output JSON with findings array." \
        --allowedTools Read Grep Bash(npm audit) \
        --json > security-report.json

    # Fail on critical issues
    - |
      CRITICAL=$(jq '[.findings[] | select(.severity == "critical")] | length' security-report.json)
      if [ "$CRITICAL" -gt 0 ]; then
        echo "Critical security issues found"
        exit 1
      fi
  artifacts:
    reports:
      sast: security-report.json
```

---

## Jenkins Pipeline Integration

```groovy
// Jenkinsfile

pipeline {
  agent any

  environment {
    CLAUDE_PATH = "${HOME}/.local/bin/claude"
  }

  stages {
    stage('Setup') {
      steps {
        sh 'curl -fsSL https://claude.ai/install.sh | bash'
      }
    }

    stage('Code Quality') {
      steps {
        script {
          sh """
            ${CLAUDE_PATH} -p "Analyze code quality metrics:
            - Cyclomatic complexity
            - Code duplication
            - Test coverage gaps

            Output JSON with metrics and recommendations." \
              --allowedTools Read Grep Bash(npm run test -- --coverage) \
              --json > quality-report.json
          """

          def report = readJSON file: 'quality-report.json'
          echo "Quality Score: ${report.score}/100"

          if (report.score < 70) {
            error("Code quality below threshold")
          }
        }
      }
    }

    stage('Security Scan') {
      steps {
        script {
          sh """
            ${CLAUDE_PATH} -p "Security vulnerability scan" \
              --allowedTools Read Grep \
              --json > security-report.json
          """

          def secReport = readJSON file: 'security-report.json'
          if (secReport.critical_count > 0) {
            error("Critical security vulnerabilities found")
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
    }
  }
}
```

---

## JSON Output Patterns

### Standard Response Format

```json
{
  "status": "success|failure",
  "summary": "High-level summary",
  "details": {
    "files_analyzed": 42,
    "issues_found": 5,
    "issues_fixed": 3
  },
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "type": "security|quality|performance",
      "file": "path/to/file.ts",
      "line": 123,
      "description": "Detailed description",
      "suggestion": "How to fix"
    }
  ],
  "metrics": {
    "coverage": 87.5,
    "complexity": 12,
    "maintainability": 75
  }
}
```

### Parsing Example

```bash
# Extract specific metrics
COVERAGE=$(jq -r '.metrics.coverage' report.json)
CRITICAL_ISSUES=$(jq '[.findings[] | select(.severity == "critical")] | length' report.json)

# Conditional logic
if [ "$CRITICAL_ISSUES" -gt 0 ]; then
  echo "Critical issues found: $CRITICAL_ISSUES"
  jq '.findings[] | select(.severity == "critical")' report.json
  exit 1
fi
```

---

## Best Practices

### Do ✅

```yaml
safety:
  - Use specific tool allowlists (not "Bash(*)")
  - Validate JSON output structure
  - Fail fast on critical issues
  - Archive artifacts for debugging
  - Use --json for programmatic consumption

performance:
  - Cache Claude Code installation
  - Limit scope (don't analyze entire codebase every time)
  - Run in parallel when possible
  - Use incremental analysis (git diff)

reliability:
  - Handle Claude errors gracefully
  - Set timeouts for long-running tasks
  - Retry transient failures
  - Log all automation actions
```

### Don't ❌

```yaml
avoid:
  - Hardcode credentials in prompts
  - Use overly permissive tool access
  - Skip validation of JSON output
  - Ignore non-critical warnings (they accumulate)
  - Run without rate limiting

security:
  - Don't commit Claude's responses without review
  - Don't expose internal paths in public repos
  - Don't trust all findings blindly (false positives exist)
```

---

## Troubleshooting

### Issue: Claude times out in CI

**Solution**:
```yaml
timeout_handling:
  - Set explicit timeout: timeout 5m claude -p "..."
  - Reduce scope: analyze changed files only
  - Use parallel jobs for independent tasks
```

### Issue: JSON output malformed

**Solution**:
```bash
# Validate JSON before parsing
if jq empty report.json 2>/dev/null; then
  echo "Valid JSON"
else
  echo "Invalid JSON output"
  cat report.json
  exit 1
fi
```

### Issue: Rate limiting

**Solution**:
```yaml
rate_limit_handling:
  - Add delays between requests: sleep 5
  - Batch operations where possible
  - Use caching for repeated analyses
```

---

## Integration with Context Engineering

### Hook Configuration

```json
{
  "hooks": {
    "PreCommit": [
      {
        "type": "bash",
        "command": ".git/hooks/pre-commit"
      }
    ],
    "PrePush": [
      {
        "type": "bash",
        "command": ".git/hooks/pre-push"
      }
    ]
  }
}
```

### CLAUDE.md Documentation

Add to project's `claude/CLAUDE.md`:

```markdown
## CI/CD Integration

This project uses Claude Code for automated quality checks:

**Git Hooks**:
- Pre-commit: Removes console.log, fixes lint errors
- Pre-push: Runs tests, security scan

**GitHub Actions**:
- PR Review: Automated security review on pull requests
- Issue Triage: Automatic labeling and classification

**Troubleshooting**:
- Check `.git/hooks/` for hook scripts
- View GitHub Actions logs for CI failures
- JSON reports in artifacts for debugging
```

---

## References

- [Anthropic Best Practices: Headless Automation](https://www.anthropic.com/engineering/claude-code-best-practices) ⭐⭐⭐⭐⭐
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- Context Engineering: CLAUDE.md, MULTI-INSTANCE-VERIFICATION.md

---

*Generated by Context Engineering Framework*
*Pattern Source: Anthropic Official Best Practices*
