# Tasks: Modernize KB Search

- [ ] **Phase 1: Foundation & Model Integration**
    - [ ] Integrate BGE-M3 model into `EmbeddingService`.
    - [ ] Implement sparse vector generation logic.
    - [ ] Verify multi-vector output (dense + sparse).

- [ ] **Phase 2: Infrastructure Upgrade**
    - [ ] Update `QdrantKnowledgeBaseRepository` to support named vectors (dense + sparse).
    - [ ] Modify `_ensure_collection` to configure sparse indexing.
    - [ ] Update `add_documents` to upsert multi-vectors.

- [ ] **Phase 3: Search Optimization**
    - [ ] Implement hybrid search in `QdrantKnowledgeBaseRepository` using both dense and sparse vectors.
    - [ ] (Optional) Update `HybridSearchUseCase` to leverage native hybrid results if suitable, or adjust RRF parameters for sparse scores.

- [ ] **Phase 4: Verification & Finalization**
    - [ ] Create ingestion script for testing BGE-M3.
    - [ ] Benchmarking: Compare search relevance with mixed Chinese/English queries.
    - [ ] Hardware Test: Verify seamless fallback from CUDA to CPU and check latency.
