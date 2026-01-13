# System Reinforcement Recommendations

Based on the goal of **"Intelligent Query"** and **"Guided Interaction"**, and an analysis of the current codebase (`orchestrator.py`, `planner.py`, `search.py`), here are the recommended areas for reinforcement:

## 1. Guided Interaction (Clarification)
**Gap:** The current `orchestrator.py` routes to `search` or `writer`. There is no dedicated state for "Asking Clarification" when a query is ambiguous.
**Action:**
- **Add `Clarification Agent`**: specialized in identifying ambiguous queries (e.g., "Where is the file?") and formulating clarifying questions to the user.
- **Update `Orchestrator` Logic**: Add a routing condition: `User Query -> Ambiguous Assessment -> (if ambiguous) -> Clarification Agent`.

## 2. Conversation Memory (Context)
**Gap:** `planner.py` accepts `context` as an argument, but `orchestrator.py` doesn't explicitly manage or retrieve conversation history from a persistent store.
**Action:**
- **Implement `ConversationRepository`**: (Infrastructure Layer) using Redis or Postgres to store chat history per Session ID.
- **Context Injection**: Ensure the `Orchestrator` fetches relevant past interaction history and injects it into the `Planner`'s context window.

## 3. Evaluation Framework (Quality Assurance)
**Gap:** While we have `evaluate_retrieval_quality` in `search.py` (Search Agent), we lack an end-to-end evaluation for "Helpfulness" or "Dialog Quality".
**Action:**
- **Add End-to-End Eval**: Create a test suite using `DeepEval` or similar to score multi-turn conversations.
- **Golden Dataset**: Build a dataset of "Ambiguous Queries" to test if the Agent correctly asks for clarification instead of hallucinating.

## 4. Infrastructure Robustness
**Gap:** The `search_agent` uses `print` or simple return values.
**Action:**
- **Structured Logging**: Ensure all Agent thoughts and decisions are logged in a structured format (JSON) for debugging logic flaws.
- **Async Safety**: Verify all external tool calls (Chroma, Google Search) are fully non-blocking to support high concurrency.
