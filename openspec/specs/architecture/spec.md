# architecture Specification

## Purpose
TBD - created by archiving change initial-onboarding. Update Purpose after archive.
## Requirements
### Requirement: Layered Multi-Agent Execution
系統 **MUST** 採用層級式的代理人架構，由一個根代理人 (Root Agent) 起始，並根據預定義的流程將任務分派給子代理人。

#### Scenario: Sequential start from guard
- **WHEN** 系統接收到使用者查詢
- **THEN** 首先執行 `guard_agent` 進行安全檢查，通過後才進入 `orchestrator_agent`

### Requirement: Iterative Retrieval and Review
系統 **SHALL** 支援檢索與審核的循環流程，在生成答案前自動驗證檢索到的上下文資訊是否足以支援回答。

#### Scenario: Insufficient information loop
- **WHEN** `reviewer_agent` 判斷檢索到的資訊不足以回答問題
- **THEN** `orchestrator_agent` 必須指示 `search_agent` 再次執行補充檢索

### Requirement: Automated Regression Testing
系統 **MUST** 具備自動化測試框架，以確保所有新功能的變更與核心檢索流程不會發生 Regression。

#### Scenario: Testing CI Pipeline
- **WHEN** 程式碼被推送或合併至 `main`
- **THEN** 必須通過單元測試 (`unit/`) 與關鍵工具整合測試 (`integration/`)
- **AND** 測試覆蓋率基準 **SHALL** 涵蓋所有 `tools/` 與 `parsers/` 目錄下的邏輯

### Requirement: Layered Architecture Enforcement
系統 **MUST** 遵循 Clean Architecture (CA) 分層原則。核心業務邏輯 (Domain & Application) 不得直接依賴於具體的技術實作 (ChromaDB, FastAPI, Gemini API)。

#### Scenario: Tech Stack Migration
- **WHEN** 需要更換向量資料庫（如從 ChromaDB 遷移至 Qdrant）
- **THEN** 僅需在 `Infrastructure` 層實作新的 Repository，且不得修改 `Application` 或 `Domain` 層的代碼。

#### Scenario: Persistence Migration
- **WHEN** 需要將 Session 儲存從 Memory 遷移至 Redis
- **THEN** 僅需抽換 `main.py` 中的 `SessionService` 實作，而不影響 Agent 核心邏輯。

### Requirement: OpenAPI Compliance
所有的外部介面端點 **SHALL** 符合 OpenAPI 3.x 規範，並提供自動生成的交互式文檔 (Swagger UI)。

#### Scenario: API Documentation Access
- **WHEN** 服務啟動後造訪 `/docs` 路徑
- **THEN** 系統必須展示完整的 API 規格、請求參數定義與回應範例

### Requirement: Intelligent Interaction
系統 **MUST** 支援導引式互動 (Guided Interaction)，允許 Agent 在資訊不足時主動向使用者提問以釐清需求，而非僅能被動回答。

#### Scenario: Ambiguous Query Clarification
- **WHEN** 使用者輸入模糊的查詢（例如「那個文件在哪？」）
- **THEN** Agent 不應直接搜尋，而應反問使用者「請問您指的是哪一份文件？或是關於哪個主題的文件？」

### Requirement: Session State Management
系統 **MUST** 具備狀態管理機制，能夠在多輪對話中維持 User 與 Agent 的交互上下文 (Session Context)。

#### Scenario: Multi-turn Context
- **WHEN** 使用者在第一輪對話提及「我的專案代碼」
- **AND** 在第二輪對話僅說「幫我總結一下」
- **THEN** Agent 必須能存取 Session 中的第一輪記憶，針對「該專案代碼」進行總結

