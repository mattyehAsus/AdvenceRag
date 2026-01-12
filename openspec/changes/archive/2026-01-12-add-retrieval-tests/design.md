# Design: Retrieval Integration Tests

## Test Strategy
由於 Reranker 模型載入較慢且可能需要外部下載，整合測試將分為兩類：
1. **Pipeline Integration (Real)**: 使用小型 Cross-Encoder 模型（如 `cross-encoder/ms-marco-MiniLM-L-6-v2`）驗證完整流程。
2. **Logic Integration (Mocked)**: Mock 掉 `rerank_results` 的回傳值，專注驗證「去重」與「切片 (top_k)」邏輯。

## Test Scenarios
1. **Exact Match vs Semantic**:
    - 資料中包含兩個文檔：A (描述 RAG 概念), B (包含版本號 "v0.5.2")。
    - 查詢 "v0.5.2" -> 預期 B 被搜出且排名靠前。
2. **Overlap Handling**:
    - 查詢 "RAG" -> Vector 與 BM25 都搜出 A。
    - 驗證結果清單長度為 1，無重複 A。
3. **Empty Results**:
    - 查詢不存在的內容 -> 驗證返回空列表且狀態為 `success`。

## Fixtures
- 使用 `conftest.py` 已有的 `mock_settings` 與 `test_data_dir`。
- 新增 `populated_db` fixture：預先填入一組具有區別性的測試文檔。
