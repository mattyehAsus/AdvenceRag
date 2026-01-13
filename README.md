# Advence RAG - Multi-Agent RAG System

基於 Google ADK 的多代理 RAG 系統，採用現代化 Python 專案結構。

## 核心願景 (Core Vision)

本專案旨在打造一個具備 **智能查詢 (Intelligent Query)** 與 **導引式互動 (Guided Interaction)** 能力的 Agent 系統。
不只是單純的問答，更透過 CRAG 與主動澄清機制，引導使用者獲取精確資訊。

## 架構特色 (Architecture)

採用 **FastAPI** 結合 **Clean Architecture**，確保系統的高擴展性與可維護性。

- **Domain Layer**: 定義 Agent 核心行為與介面，不綁定具體技術。
- **Application Layer**: 實作複雜的使用案例 (如 CRAG 檢索流程)。
- **Infrastructure Layer**: 實作具體工具 (ChromaDB, Google Search)。
- **Interface Layer**: 標準化 RESTful API (/v1/chat/completions)。

### Agent Teams
- **Orchestrator Agent**: 智慧路由與對話協調
- **Guard Agent**: 敏感資料過濾
- **Retrieval Team**: 問題分解 → 檢索 (Hybrid Search + Rerank)
- **Processing Team**: 反思驗證 → 回答生成

## 快速開始

### 安裝

```bash
# 基本安裝 (含 Chroma)
pip install -e ".[chroma]"

# 完整安裝
pip install -e ".[full]"

# 開發模式
pip install -e ".[full,dev]"
```

### 設定環境變數

```bash
cp .env.example .env
# 編輯 .env 設定 GOOGLE_API_KEY
```

### 執行

```bash
# 啟動 ADK 開發伺服器
adk web src/advence_rag

# 或使用 CLI
advence-rag --help
```

## 專案結構

```
src/advence_rag/
├── main.py           # FastAPI 應用入口
├── domain/           # 核心業務實體與介面
├── application/      # 應用邏輯 (Use Cases)
├── infrastructure/   # 外部依賴實作 (DB, AI Clients)
├── interfaces/       # API 路由 (FastAPI Routes)
└── config/           # 配置管理
```

## 文檔解析器

支援依情境選用：

| 文檔類型 | 解析器 | 安裝 |
|---------|--------|------|
| 複雜 PDF | docling | `pip install -e ".[docling]"` |
| 純文字 PDF | pymupdf4llm | `pip install -e ".[pymupdf]"` |
| Office/HTML | unstructured | `pip install -e ".[unstructured]"` |

## License

MIT
