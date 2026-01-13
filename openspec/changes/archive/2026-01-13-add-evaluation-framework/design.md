## Context
The system needs a way to verify its behavior against expected outcomes, especially for complex agent interactions like clarification and retrieval.

## Decisions
- **Golden Dataset Format**: JSON format containing `query`, `expected_category`, and `matches` (substrings for validation).
- **Execution Model**: Uses the standard ADK `Runner` to simulate user interactions asynchronously.
- **Metrics**: 
  - `pass_rate`: Percentage of cases where the actual answer matches the expected criteria.
  - `average_score`: Mean score across all test cases.

## Risks / Trade-offs
- **LLM Non-determinism**: Scores may vary slightly between runs. Mitigation: Use regex/keyword matching for objective criteria and consider LLM-based evaluation for subjective ones in the future.
