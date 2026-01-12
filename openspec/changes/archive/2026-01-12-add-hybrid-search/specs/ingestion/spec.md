## MODIFIED Requirements

### Requirement: Document Parsing Strategy
系統 **MUST** 偵測輸入文件的檔案格式，自動指派策略解析器，並在解析完成後，**SHALL** 同時更新向量索引與關鍵字索引 (BM25)。

#### Scenario: Hybrid Indexing on Ingestion
- **WHEN** 一個新的文檔被導入
- **THEN** 系統必須生成向量嵌入並存入 ChromaDB
- **AND** 系統必須將文檔分詞並更新 BM25 頻率表
