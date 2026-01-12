# Capability: Architecture

## Purpose
本規範定義了 Advence RAG 系統的層級化代理人架構與核心執行邏輯。這套架構的核心目標是透過 `root_agent` 與 `orchestrator_agent` 的層層分工，實現一個安全且具備自我修正能力的 RAG 工作流。

## ADDED Requirements

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
