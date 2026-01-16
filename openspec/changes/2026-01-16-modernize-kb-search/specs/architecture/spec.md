# Architecture Spec Delta

## MODIFIED Requirements

### Requirement: Unified Hybrid Retrieval
系統 **SHALL** 支援統一的混合檢索 (Hybrid Retrieval) 機制，結合「語義向量 (Dense Vectors)」與「關鍵字權重向量 (Sparse Vectors)」，以補足單一檢索方式的不足。

#### Scenario: Neural Keyword Weighting
- **WHEN** 進行搜尋執行時
- **THEN** 系統必須同時掃描語義向量空間與稀疏權重向量空間
- **AND** 最終排序結果 **SHALL** 整合兩者的評分，且不應僅依賴傳統的非語義分詞。

### Requirement: Multi-Vector Embedding Support
Embedding 服務 **MUST** 支援能同時生成多種向量類型的模型 (如 BGE-M3)，以簡化不同檢索模式間的資料一致性。

#### Scenario: Concurrent Vector Generation
- **WHEN** 給定一段文本進行 Embedding 加密時
- **THEN** 系統必須能夠在單次（或協調好的）請求中同時取得 Dense Vector 與 Sparse Vector。
