# AdvenceRAG 部署與配置指南

本指南說明如何管理 AdvenceRAG 的多資料庫與多向量引擎架構。系統目前支援在 **ChromaDB/Qdrant** 以及 **Gemini/Local Embedding** 之間彈性切換。

---

## 🏗️ 1. 資料庫切換 (Vector DB Switching)

系統支援動態切換存儲引擎。預設使用 ChromaDB (適合本地快速開發)，可更換為 Qdrant (適合工業級規模)。

### 切換至 Qdrant
在 `.env` 中修改：
```bash
VECTOR_DB_TYPE=qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=knowledge_base
```
> [!IMPORTANT]
> 切換資料庫後，舊的資料不會自動遷移。您需要重新執行 Ingestion 流程。

---

## 🧠 2. 向量引擎切換 (Embedding Engines)

這是系統最核心的配置。您可以選擇使用雲端 API (高品質/零資源) 或本地模型 (隱私/免費)。

### 方案 A：雲端模式 (Cloud Mode - 推薦)
適合追求最高檢索精度且不希望消耗本地資源的場景。
```bash
EMBEDDING_TYPE=cloud
EMBEDDING_MODEL=models/text-embedding-004
```

### 方案 B：本地模式 (Local Mode)
適合隱私敏感或斷網運行的場景。
```bash
EMBEDDING_TYPE=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 輕量級，CPU 友好
# 或者使用更強大的模型
# EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

---

## ⚡ 3. 混合硬體調度 (Hybrid Hardware Strategy)

AdvenceRAG 採用了 SOTA 的硬體分配策略，定義在 `docker-compose.yml` 中：

| 服務名稱 | 任務類型 | 推薦設備 | 原因 |
| :--- | :--- | :--- | :--- |
| `advence-rag` | 查詢 (Search) | **CPU** | 查詢量小，對 API 回應延遲敏感，分散 GPU 負擔。 |
| `advence-rag-ingest` | 入庫 (Ingest) | **CUDA (GPU)** | 批次處理大量文檔，使用 GPU 可加速數十倍。 |

### 如何啟用 GPU 加速？
1. 確保主機已安裝 `nvidia-container-toolkit`。
2. 在 `docker-compose.yml` 中，`advence-rag-ingest` 已預配置 `deploy.resources.reservations.devices`。
3. 啟動命令：`docker compose up --build`

---

## ⚠️ 4. 關鍵注意事項 (Critical Rules)

### 向量空間一致性 (Vector Space Integrity)
> [!CAUTION]
> **嚴禁在同一個 Collection 中混合不同的 Embedding 模型。**
> 如果您更改了 `EMBEDDING_MODEL`，您**必須**同時更改 `COLLECTION_NAME` 並重新執行入庫，否則會導致搜尋不到結果或維度報錯。

### 建議操作流程
當您想切換模型時：
1. 停止服務：`docker compose down`
2. 修改 `.env` 中的 `EMBEDDING_TYPE` 與 `EMBEDDING_MODEL`。
3. 修改 `.env` 中的 `COLLECTION_NAME` (例如從 `kb_v1` 改為 `kb_v2`)。
4. 重啟服務：`docker compose up --build`
5. 將檔案放入 `ingest/` 資料夾開始重新處理。
