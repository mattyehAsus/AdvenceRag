# Change: Add Reciprocal Rank Fusion (RRF) for Search Optimization

## Why
Currently, the hybrid search merging logic is a simple deduplication of results from vector and keyword searches. This "naive" approach doesn't leverage the relative rankings of items from both sources, often leading to suboptimal candidates being passed to the reranker. RRF is a SOTA algorithm that provides a mathematically sound way to merge multiple ranked lists without needing score normalization, significantly improving retrieval precision.

## What Changes
- **Core Search Logic**: Replace the naive merging in `HybridSearchUseCase` with an RRF-based scoring mechanism.
- **Agent Intelligence**: Update the `search_agent`'s behavior to reflect that it now uses a more sophisticated fusion strategy.
- **Rerank Optimization**: Improve the quality of top-K results by ensuring the reranker operates on the best possible hybrid candidates.

## Impact
- **Affected specs**: `agents` (search behavior), `architecture` (search requirements).
- **Affected code**: `src/advence_rag/application/use_cases/search.py`.
