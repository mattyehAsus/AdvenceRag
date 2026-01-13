## ADDED Requirements
### Requirement: Session State Management
系統 **MUST** 具備狀態管理機制，能夠在多輪對話中維持 User 與 Agent 的交互上下文 (Session Context)。

#### Scenario: Multi-turn Context
- **WHEN** 使用者在第一輪對話提及「我的專案代碼」
- **AND** 在第二輪對話僅說「幫我總結一下」
- **THEN** Agent 必須能存取 Session 中的第一輪記憶，針對「該專案代碼」進行總結

## MODIFIED Requirements
### Requirement: Layered Architecture Enforcement
系統 **MUST** 遵循 Clean Architecture (CA) 分層原則。核心業務邏輯 (Domain & Application) 不得直接依賴於具體的技術實作 (ChromaDB, FastAPI, Gemini API)。

#### Scenario: Tech Stack Migration
- **WHEN** 需要更換向量資料庫（如從 ChromaDB 遷移至 Qdrant）
- **THEN** 僅需在 `Infrastructure` 層實作新的 Repository，且不得修改 `Application` 或 `Domain` 層的代碼。

#### Scenario: Persistence Migration
- **WHEN** 需要將 Session 儲存從 Memory 遷移至 Redis
- **THEN** 僅需抽換 `main.py` 中的 `SessionService` 實作，而不影響 Agent 核心邏輯。
