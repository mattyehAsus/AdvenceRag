## 1. Setup
- [x] 1.1 Add `rank-bm25` to `pyproject.toml` dependencies
- [x] 1.2 Update local environment packages (MANUAL: Requires `rank-bm25` and `numpy`)

## 2. Infrastructure (Knowledge Base)
- [x] 2.1 Refactor `KnowledgeBaseTool` to support optional BM25 persistence
- [x] 2.2 Implement `keyword_search` method using `rank_bm25`
- [x] 2.3 Ensure `add_documents` upates both indexes atomically
- [x] 2.4 Create a migration script to build BM25 for existing data

## 3. Search Agent Enhancement
- [x] 3.1 Modify `search_knowledge_base` to execute parallel searches
- [x] 3.2 Implement result deduplication and merging
- [x] 3.3 Ensure Reranker handles merged results correctly

## 4. Verification
- [x] 4.1 Write integration tests for Hybrid Search
- [x] 4.2 Verify search quality with specific keyword queries
