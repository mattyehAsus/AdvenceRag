# Change: Infrastructure Hardening

## Why
目前系統日誌 (Logging) 僅為純文字格式，難以被機器解析以追蹤 Agent 的複雜思考流程 (Chain of Thought) 與工具呼叫狀況。此外，隨著 "Intelligent Interaction" 的引入，我们需要更嚴格的非同步 (Async) 邊界控制來避免 event loop 阻塞。

## What Changes
1.  **Structured Logging**: 引入 `python-json-logger`，將日誌標準化為 JSON 格式，包含 `trace_id`, `span_id`, `agent_name`, `tool_name` 等欄位。
2.  **Robust Async Tools**: 強制規範所有 I/O Bound 工具 (如 Search) 必須使用 `asyncio` 原生庫 (如 `httpx` 代替 `requests`)，並在架構層級加入超時熔斷機制。
3.  **Error Isolation**: 在 `orchestrator` 層級加入更細緻的 `try-except` 區塊，確保單一子 Agent 的失敗不會導致整個請求崩潰，並能產生結構化的錯誤報告。

## Impact
- **Affected Specs**: `architecture`
- **Affected Code**: `src/advence_rag/utils/log_config.py`, `src/advence_rag/infrastructure/ai/agent_service.py`
