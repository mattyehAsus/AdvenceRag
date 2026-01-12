# Proposal: Establish Testing Framework

## Motivation
目前專案缺乏結構化的測試框架，僅有分散的驗證腳本 (`verify_hybrid.py`, `repro_hang.py` 等)。為了確保核心元件（如 Hybrid Search, Ingestion Pipeline）的穩定性與未來擴展性，我們需要建立一個基於 `pytest` 的正式測試體系。

## Proposed Changes
### Infrastructure
- 建立 `tests/` 目錄結構：
  - `unit/`: 核心邏輯、設定與工具函式的單元測試。
  - `integration/`: 跨組件（如 ChromaDB + Ingestion）的整合測試。
  - `evaluation/`: 針對代理人回答質量的評估測試。
- 提供 `tests/conftest.py`：定義全域 Fixtures，如 Mock 化的配置與測試專用的臨時向量庫路徑。
- 設定 `pyproject.toml` 中的 `[tool.pytest.ini_options]` 確保測試自動發現與非同步支援。

### Specifications
- 在 `openspec/project.md` 加入測試規範。
- 在 `architecture/spec.md` 加入自動化測試的要求。

## Impact
- **Positive**: 提升開發效率，防止 Regression，確保多代理人流程的正確性。
- **Risk**: 測試維護成本，需要大量 Mock 外部 API (Gemini, Google Search)。
