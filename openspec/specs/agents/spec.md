# agents Specification

## Purpose
TBD - created by archiving change initial-onboarding. Update Purpose after archive.
## Requirements
### Requirement: Intelligent Routing
`orchestrator_agent` 以及 `search_agent` **MUST** 支援 Hybrid Search 邏輯。

#### Scenario: Hybrid Search Execution
- **WHEN** 執行檢索任務時
- **THEN** 系統必須並發調用 `vector_search` 與 `keyword_search`
- **AND** 必須使用 Reranker 或 RRF 分數進行結果融合 (Fusion)

### Requirement: Output Hallucination Prevention
`writer_agent` 的內容生成行為 **SHALL** 嚴格基於檢索小組提供的上下文資訊。

#### Scenario: Grounded Generation
- **WHEN** 生成回答時
- **THEN** 僅使用 `search_agent` 提供的知識片段，不得加入未經證實的外部知識

