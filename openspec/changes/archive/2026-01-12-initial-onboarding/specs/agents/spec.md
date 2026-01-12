# Capability: Agents

## Purpose
本文件詳細規範系統中各個專門化代理人（Agent）的具體職責、決策權限與行為準則。透過明確的代理人定義，確保系統在處理各種類型的查詢時，能有條理地運用適當的代理人完成任務。

## ADDED Requirements

### Requirement: Intelligent Routing
`orchestrator_agent` **MUST** 根據問題的性質（簡單事實型 vs. 複雜推理型）動態決定最佳的執行路徑。

#### Scenario: Simple vs Complex Routing
- **WHEN** 接收到簡單事實問題
- **THEN** 跳過 `planner_agent` 直接執行 `search_agent`
- **WHEN** 接收到需要多步驟推理的問題
- **THEN** 呼叫 `planner_agent` 進行任務分解

### Requirement: Output Hallucination Prevention
`writer_agent` 的內容生成行為 **SHALL** 嚴格基於檢索小組提供的上下文資訊。

#### Scenario: Grounded Generation
- **WHEN** 生成回答時
- **THEN** 僅使用 `search_agent` 提供的知識片段，不得加入未經證實的外部知識
