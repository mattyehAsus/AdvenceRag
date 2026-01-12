# Proposal: Add Retrieval Integration Tests

## Why
Hybrid Search 的核心優勢在於結合 Vector 與 BM25 的結果。目前的測試僅驗證了基礎的 CRUD，但未驗證 Reranking 階段的「去重邏輯」與「結果融合」是否如預期運作。透過整合測試可以確保檢索系統在處理真實查詢（包含精確關鍵字與模糊語意）時的準確性。

## What Changes
- 在 `tests/integration/` 目錄下新增 `test_retrieval_pipeline.py`。
- 針對 `advence_rag/agents/search.py` 中的 `search_knowledge_base` 進行測試：
    - **Deduplication Check**: 驗證當同一個文檔被兩種搜尋方法同時搜出時，結果清單中僅保留一份。
    - **Reranking Validation**: 驗證 Reranker 輸出的分數是否被正確應用於最終結果排序。
    - **top_k Logic**: 驗證在 Hybrid 階段取回多倍結果 (e.g., `top_k * 3`) 經 Rerank 後最終能正確切回 `top_k` 長度。

## Impact
- **Positive**: 提升檢索品質的信心，確保 Hybrid Search 不會因為重複項或錯誤的排序邏輯而降低使用者體驗。
- **Scope**: 僅限於測試程式碼，需確保測試環境能載入 Reranker 模型（或 Mock 處理）。
