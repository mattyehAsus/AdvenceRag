# architecture Specification Delta: CA Alignment

## MODIFIED Requirements

### Requirement: Layered Architecture Enforcement
系統 **MUST** 遵循 Clean Architecture (CA) 分層原則。核心業務邏輯 (Domain & Application) 不得直接依賴於具體的技術實作。

#### MODIFIED Scenario: Tech Stack Migration
- **WHEN** 需要更換基礎設施技術（如更換向量資料庫或 API 框架）
- **THEN** 僅需在 `Infrastructure` 層進行實作替換
- **AND** `Application` 層（Use Cases）與 `Domain` 層（Entities/Interfaces）不得受到影響

#### ADDED Requirement: Logic Isolation in Application Layer
所有的核心業務流程（如搜尋流程、導入流程）**MUST** 封裝在 `Application` 層中。

#### ADDED Scenario: Independent Testing
- **WHEN** 進行業務邏輯測試時
- **THEN** 必須能在不依賴 Agent 框架與具體資料庫實作的情況下測試 Use Case
