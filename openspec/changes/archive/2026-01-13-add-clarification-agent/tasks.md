# Tasks: Add Clarification Agent

- [x] Create `src/advence_rag/agents/clarification.py` with ambiguity detection logic.
- [x] Update `src/advence_rag/agents/orchestrator.py`:
    - Add `clarification_agent` routing.
    - Fix infinite loop on greetings (add termination instruction).
- [x] Verify using `tests/verify_clarification.py`.
