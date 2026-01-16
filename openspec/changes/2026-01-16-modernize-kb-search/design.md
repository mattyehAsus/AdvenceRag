# Design: BGE-M3 and Sparse Vector Integration

## Architecture Overview
The current architecture relies on a `HybridSearchUseCase` that manually calls `search_similar` and `search_keyword` and then performs Reciprocal Rank Fusion (RRF). 

By adopting BGE-M3, we shift the responsibility of "understanding keywords" from simple regex/pattern matching (or basic tokenization) to a neural model that produces sparse weights for specific tokens.

### Component Changes

#### 1. Embedding Service (Domain/Infrastructure)
- **Interface Update**: Expand `EmbeddingService` to include a method for hybrid encoding (e.g., `embed_advanced`) or allow the existing `embed_text` to return a structured object/dict if a hybrid model is configured.
- **Model Support**: Integrate BGE-M3 (potentially via `fastembed` for better CPU performance).

#### 2. Qdrant Repository (Infrastructure)
- **Named Vectors**: Collection will support `dense` and `sparse` named vectors.
- **Native Fusion**: Update search logic to use Qdrant's `prefetch` and `query_vector` for infrastructure-level fusion (RRF or Reciprocal Rank), moving this complexity out of the Application layer.
- **Backward Compatibility**: `search_similar` will now perform a hybrid search by default when BGE-M3 is active.

#### 3. Ingestion Use Case (Application)
- No changes to logic, but benefits from the improved Embedding Service performance handled in the background.

## Implementation Details

### Model Selection: BGE-M3
BGE-M3 is chosen for its native support of:
- **Dense Retrieval**: Semantic understanding.
- **Sparse Retrieval**: Neural-based keyword weighting (replacing BM25).
- **Multi-lingual**: Optimized for 100+ languages including Chinese and English.

### Hardware & Resource Management
- **Device Support**: The system will detect `cuda` vs `cpu` availability.
- **Ingestion**: Aimed at GPU usage for high-throughput batch processing.
- **Search**: Optimized for CPU/GPU. If GPU is unavailable, ONNX runtime or FP32 fallback will be used to maintain <300ms latency.

### 4. Search Complexity Management
- **Consolidation**: The `HybridSearchUseCase` is currently responsible for RRF. With Qdrant's native fusion, we can simplify this UseCase to call a single `repository.search_hybrid()` (or upgraded `search_similar`), reducing the risk of inconsistent scoring in the application layer.

## Trade-offs
- **Model Size**: BGE-M3 is larger (~2GB RAM/VRAM), requiring careful resource allocation in containerized environments.
- **Data Reconstruction**: Existing points in Qdrant must be re-indexed to populate the sparse vector field. The user will handle this manually by clearing the collection and re-ingesting documents.
- **Dependency**: No extra tokenization libraries like HanLP or Jieba are required for search, simplifying the stack. Using `fastembed` adds a dependency but provides optimized ONNX runtimes.

## Alternatives Considered
- **HanLP/Jieba Pre-tokenization**: Decided against as it lacks neural context for keywords and adds more external dependencies.
