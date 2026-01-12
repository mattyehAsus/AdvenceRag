# Design: Testing Framework

## Testing Stack
- **Framework**: `pytest`
- **Asynchronous**: `pytest-asyncio`
- **Mocking**: `unittest.mock` 及 `pytest-mock`
- **Coverage**: `pytest-cov` (可選)

## Directory Structure
```text
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
│   ├── test_config.py
│   ├── test_utils.py
│   └── test_parsers.py
├── integration/         # Integration tests
│   ├── test_knowledge_base.py
│   └── test_ingestion.py
└── evaluation/          # Agent behavior evaluation
    └── test_search_agent.py
```

## Global Fixtures (`conftest.py`)
1. `mock_settings`: 覆蓋預設 `Settings`，將 `chroma_persist_directory` 指向臨時目錄。
2. `test_chroma`: 初始化一個乾淨的臨時 Chroma 資料夾。
3. `sample_docs`: 提供一組標準的人造測試文件。

## Testing Conventions
- **Naming**: 檔案必須以 `test_` 開頭，函式也必須以 `test_` 開頭。
- **Marks**:
  - `@pytest.mark.asyncio`: 用於非同步測試。
  - `@pytest.mark.integration`: 用於需要外部依賴或較慢的測試。
  - `@pytest.mark.agent`: 專用於多代理人流程測試。

## Implementation Path
1. 配置 `pyproject.toml` 中的 `[tool.pytest.ini_options]`。
2. 建立 `tests/conftest.py` 及基礎目錄。
3. 實作單元測試樣板。
4. 遷移現有的驗證腳本到 `tests/` 下。
