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

