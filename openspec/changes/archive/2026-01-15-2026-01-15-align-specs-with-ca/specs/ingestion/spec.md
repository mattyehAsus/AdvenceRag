# ingestion Specification Delta: CA Alignment

## MODIFIED Requirements

### Requirement: Document Parsing Strategy
系統 **MUST** 偵測輸入文件的檔案格式，自動指派策略解析器，並在解析完成後，**SHALL** 同時更新「向量存儲」與「關鍵字索引」。

#### MODIFIED Scenario: Hybrid Indexing on Ingestion
- **WHEN** 一個新的文檔被導入
- **THEN** 系統必須生成向量嵌入並存入「向量存儲」實作 (Vector Storage Implementation)
- **AND** 系統必須將文檔分詞並更新關鍵字頻率表

### Requirement: Vector Storage Consistency
所有解析後的文本片段在存入向量資料庫時，**SHALL** 包含與原始文件對應的元數據 (Metadata)。

#### MODIFIED Scenario: Metadata Persistence
- **WHEN** 文檔被存入「向量存儲」時
- **THEN** 必須包含來源檔名、頁碼及原始文字片段等追蹤資訊
