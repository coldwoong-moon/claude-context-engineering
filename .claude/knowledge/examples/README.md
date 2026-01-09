# Dynamic Few-Shot Examples System

## Overview

작업 컨텍스트에 기반하여 가장 관련성 높은 예제를 동적으로 선택하여 페르소나 context에 주입.

## Architecture

```yaml
selection_strategy:
  task_similarity:
    method: cosine_similarity
    embeddings: task_description_vectors
    threshold: 0.75

  success_rate:
    metric: historical_performance
    weight: 0.3
    min_success_rate: 0.8

  recency:
    preference: recent_successful_patterns
    weight: 0.2
    decay_days: 30

scoring:
  total_score = similarity * 0.5 + success_rate * 0.3 + recency * 0.2
  select_top_k: 3
```

## Example Structure

```markdown
---
id: example-001
task_type: refactoring
persona: refactorer
domain: backend
language: typescript
success_rate: 0.92
created: 2025-01-09
tags: [solid, dry, optimization]
---

# Example: Extract Service Class

## Context
Large controller with business logic mixed in.

## Before
```typescript
class UserController {
  async createUser(req, res) {
    // 50+ lines of business logic
    const validation = ...
    const hashing = ...
    const db = ...
  }
}
```

## After
```typescript
class UserService {
  async create(userData: CreateUserDto): Promise<User> {
    // Clean, testable business logic
  }
}

class UserController {
  constructor(private userService: UserService) {}

  async createUser(req, res) {
    const user = await this.userService.create(req.body);
    res.json(user);
  }
}
```

## Outcome
- Lines reduced: 50 → 15 in controller
- Testability: +80%
- Reusability: +100%

## Lessons
1. Separate concerns: controller ≠ business logic
2. Injectable services for testing
3. Type-safe DTOs for validation
```

## Directory Structure

```
.claude/knowledge/examples/
├── README.md                    # This file
├── index.json                   # Example registry with metadata
├── refactoring/
│   ├── extract-service.md
│   ├── eliminate-duplication.md
│   └── simplify-conditionals.md
├── architecture/
│   ├── api-design.md
│   ├── event-driven.md
│   └── microservice-boundaries.md
├── security/
│   ├── auth-implementation.md
│   ├── input-validation.md
│   └── secure-storage.md
├── performance/
│   ├── query-optimization.md
│   ├── caching-strategy.md
│   └── async-patterns.md
└── frontend/
    ├── component-composition.md
    ├── state-management.md
    └── accessibility.md
```

## Example Registry (index.json)

```json
{
  "version": "1.0",
  "examples": [
    {
      "id": "example-001",
      "file": "refactoring/extract-service.md",
      "task_type": "refactoring",
      "persona": "refactorer",
      "domain": "backend",
      "language": "typescript",
      "tags": ["solid", "dry", "optimization"],
      "success_rate": 0.92,
      "usage_count": 15,
      "created": "2025-01-09",
      "last_used": "2025-01-09",
      "embedding_vector": null
    }
  ],
  "statistics": {
    "total_examples": 0,
    "avg_success_rate": 0.0,
    "most_used_persona": null,
    "last_updated": "2025-01-09T14:00:00Z"
  }
}
```

## Usage Flow

```
┌────────────────────────────────────────────────────────────┐
│         DYNAMIC FEW-SHOT EXAMPLE SELECTION                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Task Analysis                                          │
│     ↓                                                      │
│  2. Extract: task_type, domain, language, keywords        │
│     ↓                                                      │
│  3. Search Examples (similarity > 0.75)                    │
│     ↓                                                      │
│  4. Score Candidates                                       │
│     - Similarity: 50%                                      │
│     - Success rate: 30%                                    │
│     - Recency: 20%                                         │
│     ↓                                                      │
│  5. Select Top 3                                           │
│     ↓                                                      │
│  6. Inject into Persona Context                           │
│     ↓                                                      │
│  7. Execute Task with Examples                            │
│     ↓                                                      │
│  8. Record Outcome                                         │
│     ↓                                                      │
│  9. Update Success Rates                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Integration

### Persona Context Injection
```markdown
**Relevant Examples**:

**Example 1**: Extract Service Class (success: 92%, used: 15x)
[condensed example with key patterns]

**Example 2**: Eliminate Duplication (success: 88%, used: 23x)
[condensed example with key patterns]

**Example 3**: Simplify Conditionals (success: 85%, used: 19x)
[condensed example with key patterns]

---
**Current Task**: [task description]
```

### Example Collection Hook
```yaml
post_task_completion:
  - evaluate_quality
  - if quality >= 0.8:
      - extract_example
      - add_to_registry
      - update_statistics
```

## Seed Examples

초기 예제 세트 (각 페르소나별 3-5개):
- **Refactorer**: SOLID principles, DRY, KISS
- **Architect**: System design, API design, scalability
- **Security**: Auth patterns, input validation, secure storage
- **Performance**: Query optimization, caching, async patterns
- **Frontend**: Component patterns, state management, accessibility

## Metrics

```yaml
effectiveness:
  task_completion_speed: "% improvement"
  success_rate: "% of tasks completed successfully"
  pattern_reuse: "% of examples actually used"

quality:
  example_relevance: "avg similarity score"
  success_rate_accuracy: "actual vs predicted"
```

## Implementation Status

- [x] Directory structure
- [x] Architecture defined
- [x] Selection algorithm
- [x] Example template
- [x] Registry schema
- [ ] Seed examples creation
- [ ] Similarity function
- [ ] Integration with personas
- [ ] Collection hooks

## Expected Impact

**Speed Improvement**: +25% faster task completion
**Pattern Reuse**: 70%+ example utilization rate
**Quality**: Consistent patterns across similar tasks

## Next Steps

1. Create seed examples (15-20 total)
2. Implement similarity function
3. Build example registry
4. Integrate with persona system
5. Add collection hooks
6. Test with real tasks
