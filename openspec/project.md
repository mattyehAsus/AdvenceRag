# Project Context

## Purpose
Advence RAG 是一個基於 Google ADK (Agent Development Kit) 的多代理 (Multi-Agent) 檢索增強生成 (RAG) 系統。目標是透過多個專門代理人（如協調、安全、檢索、審核、生成）的協同合作，提供高品質、安全且可靠的問答服務。

## Tech Stack
- **語言**: Python 3.11+ (使用 `uv` 管理)
- **核心框架**: Google ADK, Google GenAI
- **向量資料庫**: ChromaDB
- **文檔解析**: Docling, PyMuPDF4LLM, Unstructured (Strategy Pattern)
- **資料驗證**: Pydantic v2
- **排程**: APScheduler
- **重排序**: Sentence-Transformers

## Project Conventions

### Code Style
- **Linter/Formatter**: Ruff (Line length: 100, Target version: py311)
- **Type Checking**: Mypy (Strict mode)
- **Naming**: 遵循 PEP 8 規範。Agent 定義通常以 `_agent` 結尾。

### Architecture Patterns
- **Multi-Agent Orchestration**: 使用 `SequentialAgent` 與 `Agent` 建構層級化的代理系統。
- **Strategy Pattern**: 文檔解析器根據檔案類型與需求情境動態切換。
- **Configuration**: 使用 `pydantic-settings` 進行配置管理，支援 `.env`。

### Testing Strategy
- **框架**: Pytest
- **異步測試**: `pytest-asyncio`
- **結構**: 測試案例存放於 `tests/` 目錄。

### Git Workflow
[尚未定義具體分支策略，預設為主幹開發模式]

## Domain Context
- **RAG**: 檢索增強生成，結合檢索與 LLM 生成能力。
- **Agentic Workflow**: 將複雜任務拆解為多個 Agent 的對話與協作。

## Important Constraints
- 必須遵循 ADK 的代理定義模式。
- 檢索結果必須經過 Reviewer Agent 驗證。

## External Dependencies
- Google AI (Gemini) API
- ChromaDB (Local or Server)
