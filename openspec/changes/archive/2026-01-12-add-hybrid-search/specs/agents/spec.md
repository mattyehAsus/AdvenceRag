## MODIFIED Requirements

### Requirement: Intelligent Routing
`orchestrator_agent` 以及 `search_agent` **MUST** 支援 Hybrid Search 邏輯。

#### Scenario: Hybrid Search Execution
- **WHEN** 執行檢索任務時
- **THEN** 系統必須並發調用 `vector_search` 與 `keyword_search`
- **AND** 必須使用 Reranker 或 RRF 分數進行結果融合 (Fusion)
