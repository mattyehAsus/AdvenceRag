# Architecture Specification - Testing Additions

## ADDED Requirements
### Requirement: Automated Regression Testing
系統 **MUST** 具備自動化測試框架，以確保所有新功能的變更與核心檢索流程不會發生 Regression。

#### Scenario: Testing CI Pipeline
- **WHEN** 程式碼被推送或合併至 `main`
- **THEN** 必須通過單元測試 (`unit/`) 與關鍵工具整合測試 (`integration/`)
- **AND** 測試覆蓋率基準 **SHALL** 涵蓋所有 `tools/` 與 `parsers/` 目錄下的邏輯
