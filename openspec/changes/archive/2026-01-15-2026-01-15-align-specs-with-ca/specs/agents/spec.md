# agents Specification Delta: CA Alignment

## MODIFIED Requirements

### Requirement: Intelligent Routing
代理人（如 `search_agent`）**MUST** 透過調用專門的 `Application` 層 Use Case 來執行檢索任務，而非自行實現搜尋邏輯。

#### MODIFIED Scenario: Hybrid Search Execution
- **WHEN** 代理人需要執行搜尋時
- **THEN** 必須調用 `HybridSearchUseCase`（或同等層級的服務）
- **AND** 使用該 Use Case 提供的統合搜尋能力（含並發檢索與 Fusion）
