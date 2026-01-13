# Proposal: Add Clarification Agent for Ambiguous Queries

## 1. Context & Motivation
Currently, the system attempts to answer all queries, even vague ones (e.g., "Where is the file?"), leading to potential hallucinations or generic searches. We need a mechanism to identify ambiguity and ask the user for more details before proceeding.

## 2. Proposed Changes
- **New Agent**: `ClarificationAgent` specialized in detecting ambiguity.
- **Orchestration Update**: 
    - Modify `OrchestratorAgent` to invoke `ClarificationAgent` when the user's intent is unclear.
    - **Robustness Fix**: Explicitly instruct `Orchestrator` to terminate conversation after `WriterAgent` handles a greeting (fixing infinite loop bug).

## 3. Impact Analysis
- **User Experience**: Users will be guided to provide better input, improving final answer quality.
- **Architecture**: Adds a new routing Node in the Orchestrator graph.
- **Performance**: One extra LLM call for ambiguous queries (acceptable trade-off for accuracy).

## 4. Alternatives Considered
- **Prompt Engineering**: Just telling the Orchestrator to "ask back" often fails as it tries to multitask (search + plan). A dedicated agent is more robust.
