# Ingestion Spec Delta

## MODIFIED Requirements

### Requirement: Document Parsing Strategy
系統 **MUST** 偵測輸入文件的檔案格式，自動指派策略解析器，並在解析完成後，**SHALL** 同時更新「向量存儲」中的「多維向量索引 (Multi-vector Indexing)」。

#### MODIFIED Scenario: Neural Hybrid Indexing on Ingestion
- **WHEN** 一個新的文檔被導入
- **THEN** 系統必須生成語義向量 (Dense) 並存入向量存儲
- **AND** 系統必須利用模型生成稀疏向量 (Sparse/Neural Keywords) 並同步存入相同點位 (Point)
- **AND** 此過程不應依賴外部靜態分詞庫 (如 Jieba)，轉而依賴 Embedding 模型自帶的研究邏輯。
