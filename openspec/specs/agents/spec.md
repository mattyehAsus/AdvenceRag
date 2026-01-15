# agents Specification

## Purpose
TBD - created by archiving change initial-onboarding. Update Purpose after archive.
## Requirements
### Requirement: Intelligent Routing
代理人（如 `search_agent`）**MUST** 透過調用專門的 `Application` 層 Use Case 來執行檢索任務，而非自行實現搜尋邏輯。

#### MODIFIED Scenario: Hybrid Search Execution
- **WHEN** 代理人需要執行搜尋時
- **THEN** 必須調用 `HybridSearchUseCase`（或同等層級的服務）
- **AND** 使用該 Use Case 提供的統合搜尋能力（含並發檢索與 Fusion）

### Requirement: Output Hallucination Prevention
`writer_agent` 的內容生成行為 **SHALL** 嚴格基於檢索小組提供的上下文資訊。

#### Scenario: Grounded Generation
- **WHEN** 生成回答時
- **THEN** 僅使用 `search_agent` 提供的知識片段，不得加入未經證實的外部知識

