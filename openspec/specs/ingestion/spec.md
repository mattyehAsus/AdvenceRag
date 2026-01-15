# ingestion Specification

## Purpose
TBD - created by archiving change initial-onboarding. Update Purpose after archive.
## Requirements
### Requirement: Document Parsing Strategy
系統 **MUST** 偵測輸入文件的檔案格式，自動指派策略解析器，並在解析完成後，**SHALL** 同時更新「向量存儲」與「關鍵字索引」。

#### MODIFIED Scenario: Hybrid Indexing on Ingestion
- **WHEN** 一個新的文檔被導入
- **THEN** 系統必須生成向量嵌入並存入「向量存儲」實作 (Vector Storage Implementation)
- **AND** 系統必須將文檔分詞並更新關鍵字頻率表

### Requirement: Lifecycle Management for Ingested Files
入庫管道 **MUST** 自動管理已處理檔案的生命週期，避免重複處理並維持目錄整潔。

#### Scenario: Successful Archiving
- **WHEN** 檔案處理成功並完成索引
- **THEN** 系統必須將該檔案搬移至 `processed/` 子目錄。

#### Scenario: Failure Archiving
- **WHEN** 檔案處理因錯誤而失敗
- **THEN** 系統必須將該檔案搬移至 `error/` 子目錄。

### Requirement: Diagnostic Logging for Ingestion Failures
對於處理失敗的檔案，系統 **SHALL** 產生對應的診斷日誌。

#### Scenario: Error Log Generation
- **WHEN** 檔案被搬移至 `error/` 目錄時
- **THEN** 系統必須建立一個對應的 `.log` 檔案，記錄錯誤訊息與時間。

### Requirement: Immediate Ingestion Scan
背景入庫排程器 **SHALL** 在服務啟動時立即執行一次掃描。

#### Scenario: Startup Processing
- **WHEN** Ingest 服務啟動時
- **THEN** 必須在進入定期循環前，優先執行一次完整的目錄掃描。

### Requirement: Vector Storage Consistency
所有解析後的文本片段在存入向量資料庫時，**SHALL** 包含與原始文件對應的元數據 (Metadata)。

#### MODIFIED Scenario: Metadata Persistence
- **WHEN** 文檔被存入「向量存儲」時
- **THEN** 必須包含來源檔名、頁碼及原始文字片段等追蹤資訊

