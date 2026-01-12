# Change: Add Hybrid Search (Vector + BM25)

## Why
目前的檢索系統僅依賴向量搜尋 (Vector Search)，這在處理語意相似性時表現良好，但在處理「精確關鍵字」（如產品型號、專業術語、數字）時容易產生誤差。透過加入 BM25 關鍵字搜尋並實作 Hybrid Search，可以顯著提升檢索的召回率 (Recall) 與精確度。

## What Changes
- [NEW] 引入 `rank_bm25` 庫用於關鍵字索引與搜尋。
- [MODIFY] `KnowledgeBaseTool`: 增加 BM25 索引的建立與維護邏輯。
- [MODIFY] `search_agent`: 修改檢索流程，併行執行向量與關鍵字搜尋，並使用 RRF (Reciprocal Rank Fusion) 或 Reranker 進行結果融合。
- [MODIFY] `Ingestion Pipeline`: 在導入文檔時同步更新 BM25 索引。

## Impact
- **BREAKING**: `search_similar` 工具的返回結構可能會增加搜尋類型的元數據。
- 效能：索引建立時間會略微增加，但檢索時延仍保持在可接受範圍。
- 儲存：需要額外的磁碟空間來存儲 BM25 字典與頻率表。
