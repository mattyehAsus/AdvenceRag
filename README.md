# Advence RAG - Multi-Agent RAG System

基於 Google ADK 的多代理 RAG 系統，採用現代化 Python 專案結構。

## 架構特色

- **Orchestrator Agent**: 智慧路由與對話協調
- **Guard Agent**: 敏感資料過濾
- **Retrieval Team**: 問題分解 → 檢索 → Rerank
- **Processing Team**: 反思驗證 → 回答生成
- **Optimization Team**: 背景文檔處理與向量化

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
├── agent.py          # ADK 入口點 (root_agent)
├── agents/           # Agent 定義
├── tools/            # 自定義工具
├── parsers/          # 文檔解析器 (Strategy Pattern)
├── workflows/        # 工作流程
├── config/           # 配置管理
└── utils/            # 工具函數
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
