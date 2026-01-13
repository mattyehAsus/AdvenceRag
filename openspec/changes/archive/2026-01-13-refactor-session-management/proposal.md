# Change: Refactor Session Management

## Why
目前 `OrchestratorAgentService` 於每次請求時重新實例化，導致 `InMemorySessionService` 遺失狀態。為了支援未來的「導引式互動」與「隱藏上下文」需求，我們需要一個穩定的 Session 管理機制。

## What Changes
1.  **Singleton Pattern**: 修改 `main.py` 的依賴注入邏輯，將 `AgentService` 重構為 Singleton，確保 `InMemorySessionService` 在應用程式生命週期內存活。
2.  **Interface Segregation**: 定義明確的 `SessionService` 介面，為未來遷移至 `SQLite/Redis` (Persistence) 做準備。
3.  **Refactor**: 修改 `infrastructure/ai/agent_service.py` 以支援外部注入 Session Service。

## Impact
- **Affected Specs**: `architecture`
- **Affected Code**: `src/advence_rag/main.py`, `src/advence_rag/interfaces/api/v1/chat.py`, `src/advence_rag/infrastructure/ai/agent_service.py`
