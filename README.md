# Advence RAG - Multi-Agent RAG System

基於 Google ADK 的多代理 RAG 系統，採用現代化 Python 專案結構。

## 核心願景 (Core Vision)

本專案旨在打造一個具備 **智能查詢 (Intelligent Query)** 與 **導引式互動 (Guided Interaction)** 能力的 Agent 系統。
不只是單純的問答，更透過 CRAG 與主動澄清機制，引導使用者獲取精確資訊。

## 架構特色 (Architecture)

採用 **FastAPI** 結合 **Clean Architecture**，確保系統的高擴展性與可維護性。
同時具備 **Service Splitting** 能力，將單一應用拆分為輕量級搜尋服務與重型入庫服務。

- **Domain Layer**: 定義 Agent 核心行為與介面，不綁定具體技術。
- **Application Layer**: 實作複雜的使用案例 (如 RRF 檢索、非同步入庫)。
- **Infrastructure Layer**: 實作具體工具 (ChromaDB, Qdrant, Gemini/Local Embeddings)。
- **Interface Layer**: 標準化 RESTful API (/v1/chat/completions) 與 Ingest Endpoints。

### Agent Teams
- **Orchestrator Agent**: 智慧路由與對話協調 (具備 Ambiguity Detection)
- **Guard Agent**: 敏感資料過濾與安全檢查
- **Search Agent**: CRAG 檢索專家 (支援 RRF 融合與 Web Search 備援)
- **Reviewer Agent**: 反思驗證團隊 (迭代審核資料充分性)
- **Writer Agent**: 回答生成專家 (遵循 Grounded Generation 原則)

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

#### 推薦：Docker Compose (生產/完整模式)
```bash
# 一鍵啟動 (含 Qdrant, Search Service, Ingest Worker)
docker compose up --build
```

#### 開發模式
```bash
# 啟動 ADK 視覺化開發 UI
adk web src/advence_rag

# 或使用 CLI 啟動入庫掃描器
advence-rag scheduler --watch ./data/ingest
```

## 🔧 進階配置
詳細配置請參考：**[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
- **多資料庫**: 切換 `VECTOR_DB_TYPE=qdrant` 或 `chroma`。
- **向量引擎**: 切換 `EMBEDDING_TYPE=cloud` (Gemini) 或 `local` (CPU/GPU)。
- **硬體調度**: 搜尋用 CPU，入庫用 GPU (詳見 Docker 配置)。

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
