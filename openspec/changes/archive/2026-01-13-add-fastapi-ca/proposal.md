# Proposal: FastAPI with Clean Architecture Integration

## Why
目前專案以基礎腳本與類別為主，缺乏對外提供服務的統一口徑。為了讓 Advence RAG 具備擴展開發的能力，我們需要建立一個標準化、低耦合的架構。
FastAPI 深度整合了 OpenAPI 規格，能自動生成 Swagger 文件，並提供極佳的非同步處理能力，適合 RAG 這類高 I/O 密集的應用。

## What Changes
1.  **引進 FastAPI**: 建立 `src/advence_rag/main.py` 作為服務入口。
2.  **重整架構 (Clean Architecture)**:
    *   `src/advence_rag/domain`: 存放實體與介面定義。
    *   `src/advence_rag/application`: 包含 Use Cases (位於 `use_cases/` 子目錄)。
    *   `src/advence_rag/infrastructure`:
        *   `ai/`: `agent_service.py`, `reranker_service.py`。
        *   `persistence/`: `hybrid_repository.py`。
        *   `parsers/`: 文件解析實作。
    *   `src/advence_rag/interfaces`:
        *   `api/v1/`: `chat.py`, `ingest.py`, `schemas.py`。
3.  **依賴注入 (DI)**: 於 `main.py` 與 Router 中組裝依賴。
4.  **OpenAPI 規格**: 實作 `/v1/chat/completions` (OpenAI 相容) 與 `/api/v1/ingest`。

## Impact
*   **Positive**: 提升開發效率、增強系統可維護性、易於實現 CI/CD 與單元測試。
*   **Scope**: 核心檢索與解析代碼已移動至 `infrastructure` 層，對外介面標準化。
