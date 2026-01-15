# Proposal: Unified Search Architecture

## Goal
Unify the fragmented search logic by migrating agent-based retrieval (CRAG, formatting) into a clean, reusable application layer (`HybridSearchUseCase`). This improves testability, maintainability, and architectural consistency.

## Context
Previously, `SearchAgent` implemented hybrid search, reranking, and CRAG fallback logic directly using low-level tools. Simultaneously, a `HybridSearchUseCase` existed but lacked these critical features. This fragmentation led to duplicated logic and made it difficult to verify search behavior independently of the agent framework.

## Proposed Changes
- **Domain Layer**: Introduce `WebSearchService` interface for external search fallback.
- **Infrastructure Layer**: Implement `SerperWebSearchService` and upgrade `CrossEncoderReranker` to be async-compatible.
- **Application Layer**: Enhance `HybridSearchUseCase` to handle the full retrieval cycle:
    - Parallel Vector + Keyword search.
    - Result merging and deduplication.
    - Cross-Encoder reranking.
    - Evaluation of result quality (CRAG threshold).
    - Web search fallback if needed.
    - Result formatting for LLM consumption.
- **Agent Layer**: Refactor `SearchAgent` to delegate all retrieval logic to the `HybridSearchUseCase`.

## Benefits
- **Clean Architecture**: Retrieval logic is decoupled from the agent framework.
- **Testability**: `HybridSearchUseCase` can be unit tested without starting agents or LLMs.
- **Reusability**: The core search flow can be used by other parts of the system (e.g., standard API endpoints) without modification.
- **Improved Retrieval**: Full integration of CRAG and hybrid search ensures consistent result quality.
