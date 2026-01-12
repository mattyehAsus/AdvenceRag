# Design: Hybrid Search Implementation

## Context
我們需要在現有的 Chroma 向量資料庫基礎上，增加一個全文檢索 (Full-text Search) 引擎。由於 Chroma 目前對精確關鍵字搜尋的支援較弱，我們選擇實作一個基於 `rank_bm25` 的外部索引。

## Goals
- 提供可靠的關鍵字匹配能力。
- 實作向量與關鍵字的結果融合。
- 保持 Ingestion Pipeline 的簡單性。

## Decisions

### 1. BM25 實作方式
我們將使用 `rank_bm25` 庫。
- **儲存**: BM25 的模型 (Corpus, Frequencies) 將被序列化並存儲在 Chroma 相同的持久化目錄下（例如 `chroma_db/bm25_index.pkl`）。
- **分詞 (Tokenization)**: 使用簡單的空白分詞或與 LLM 相容的分詞器（如 `tiktoken` 或是 `jieba` 如果涉及中文）。

### 2. 結果融合 (Fusion Strategy)
我們將採用 **Reciprocal Rank Fusion (RRF)** 或直接利用現有的 **Cross-Encoder Reranker**。
- **方案**: `search_agent` 同時從兩個索引獲取 Top-50 結果，將它們去重合併後，交由 `rerank_results` 進行最終排名。

## Migration Plan
1.  安裝 `rank_bm25` 依賴。
2.  修改 `add_documents` 工具，在寫入 Chroma 的同時將文本加入 BM25 索引。
3.  實作 `rebuild_bm25_index` 腳本，用於將現有向量庫中的資料建立初始關鍵字索引。

## Risks / Trade-offs
- **記憶體占用**: BM25 模型在執行時需要載入記憶體。對於極大型資料庫，需要考慮分片或改用更重型的搜尋引擎（如 Meilisearch 或 Qdrant）。
- **同步問題**: 需確保 Chroma 與 BM25 索引在新增/刪除文件時保持同步。

## Database Portability (Future-proofing)
考慮到未來可能遷移至 **Qdrant** 等原生支援 Hybrid Search 的向量資料庫：
1. **Interface Abstraction**: 我們將在 `KnowledgeBaseTool` 中封裝 `search_hybrid(query)` 方法，`search_agent` 僅呼叫此標準介面，不介入具體的 RRF 或並行邏輯。
2. **Modular Components**: BM25 邏輯將被封裝在獨立的類別或模組中。
3. **Migration Path to Qdrant**: 
    - 若決定遷移，僅需替換 `KnowledgeBaseTool` 的實作。
    - Qdrant 支援 Sparse Vectors 實作 BM25，屆時可移除 `rank-bm25` 庫，改由 Qdrant 伺服器端處理融合 (Fusion)，程式碼邏輯將會進一步精簡。
    - 遷移工作量主要在於資料重啟導入 (Re-ingestion) 以生成 Sparse Vectors。
