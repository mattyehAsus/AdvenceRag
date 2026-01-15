# Tasks: Unified Search Architecture

- [x] Analyze current retrieval logic in `SearchAgent` and `HybridSearchUseCase`. <!-- id: 0 -->
- [x] Define `WebSearchService` interface in domain layer. <!-- id: 1 -->
- [x] Implement `SerperWebSearchService` in infrastructure layer. <!-- id: 2 -->
- [x] Refactor `CrossEncoderReranker` to support async execution. <!-- id: 3 -->
- [x] Enhance `HybridSearchUseCase` with CRAG fallback, quality evaluation, and LLM-friendly formatting. <!-- id: 4 -->
- [x] Add `CRAG_ENABLED` setting to application configuration. <!-- id: 5 -->
- [x] Refactor `SearchAgent` to delegate retrieval tasks to `HybridSearchUseCase`. <!-- id: 6 -->
- [x] Verify implementation via unit tests and end-to-end `curl` testing. <!-- id: 7 -->
