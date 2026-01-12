# ingestion Specification

## Purpose
TBD - created by archiving change initial-onboarding. Update Purpose after archive.
## Requirements
### Requirement: Document Parsing Strategy
系統 **MUST** 偵測輸入文件的檔案格式（如 PDF, Docx, HTML 等），並自動指派最適當的策略解析器 (Strategy Parser) 進行處理。

#### Scenario: Complex PDF Parsing
- **WHEN** 處理含有複雜表格或佈局的 PDF 檔案
- **THEN** 應選用 `DoclingParser` 進行精確解析

### Requirement: Vector Storage Consistency
所有解析後的文本片段在存入向量資料庫時，**SHALL** 包含與原始文件對應的元數據 (Metadata)。

#### Scenario: Metadata Persistence
- **WHEN** 文檔被存入 ChromaDB
- **THEN** 必須包含來源檔名、頁碼及原始文字片段等追蹤資訊

