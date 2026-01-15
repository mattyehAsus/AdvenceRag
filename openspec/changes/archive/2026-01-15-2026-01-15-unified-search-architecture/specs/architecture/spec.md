# Architecture Specification Delta: Unified Search

## MODIFIED Requirements

### Requirement: Layered Architecture Enforcement
系統 **MUST** 遵循 Clean Architecture (CA) 分層原則。核心業務邏輯 (Domain & Application) 不得直接依賴於具體的技術實作 (ChromaDB, FastAPI, Gemini API)。

#### ADDED Scenario: Unified Search Logic
- **GIVEN** 系統需要執行複合式搜尋（混合搜尋、重排序、CRAG 備援）
- **WHEN** 搜尋請求發出時
- **THEN** 所有的核心搜尋邏輯必須封裝在 `Application` 層的 Use Case 中
- **AND** 該 Use Case 必須透過 `Domain` 介面（如 `WebSearchService`）與外部服務交互
- **AND** `SearchAgent` 必須僅負責調用該 Use Case 並展示結果，不得包含檢索邏輯的具體實作
