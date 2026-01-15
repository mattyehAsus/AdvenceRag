# AdvenceRAG Technical Brief

AdvenceRAG 是一個基於 Clean Architecture 與 SOTA (State-Of-The-Art) 檢索技術構建的高性能 RAG 系統。其設計核心在於將「高頻查詢」與「重型入庫」解耦，並極大化檢索精度與工程穩定性。

## 🌟 核心特性 (Core Characteristics)

### 1. 專業級服務拆分 (Service Decoupling)
系統採用「軟切分」架構，將單一應用拆分為兩個專注的服務，平衡了部署靈活性與體積：
- **搜尋服務 (Search Service)**: **極輕量級 (1.82GB)**，專注於 API 回應與檢索。使用 CPU 最佳化版 PyTorch，確保在不需要 GPU 的環境下也能執行高品質的 Reranking。
- **入庫服務 (Ingest Service)**: **重型任務處理 (8.94GB)**，支援 GPU 加速及多種 OCR 解析引擎（Docling, Unstructured），專門處理複雜的文件解析。

### 2. 多智能體協作架構 (Multi-Agent Intelligence)
系統的核心大腦採用了領域領先的 Multi-Agent 自律協作模型，而非單一的線性流程：
- **Orchestrator (總調度器)**: 負責全局狀態管理，就像交響樂團的指揮，決定何時該調用哪個專家 Agent。同時具備 **Ambiguity Detection** 能力，對於模糊需求會主動發起「導引式提問」以釐清目標。
- **Guard Agent (安全衛士)**: 第一道防線，執行敏感資訊過濾與合規性檢查，確保系統安全。
- **Planner Agent (策略專家)**: 將複雜的用戶問題拆解成多個可執行的搜尋任務，並規劃最佳解題路徑。
- **Search Agent (檢索專家)**: 具備工具呼叫 (Tool Calling) 能力，能自主切換向量資料庫與網路搜尋，獵取最相關資訊。
- **Reviewer Agent (審核專家)**: 扮演「批判者」角色，執行 **Iterative Review**。若判斷資訊不足，會指示重啟檢索流程，實現「自我糾錯」閉環。
- **Writer Agent (生成專家)**: 負責最終答案的撰寫。遵循 **Grounded Generation** 原則，嚴格限制僅使用檢索所得資訊，徹底杜絕 AI 幻覺 (Hallucination)。

### 3. SOTA 混合檢索與重排 (Hybrid Search & Reranking)
系統不只依賴向量搜尋，而是透過多層過濾確保答案精準度：
- **Hybrid Search**: 結合了向量語義搜尋 (Semantic Search) 與關鍵字搜尋 (BM25/Full-text)，解決專有名詞與縮寫的檢索痛點。
- **RRF 分數融合 (Reciprocal Rank Fusion)**: 內建業界標準的 RRF 演算法，將不同來源的檢索結果進行數學上的最優化融合，克服不同評分標準的偏差。
- **混合資料庫支援 (Multi-DB Architecture)**: 支援動態切換向量資料庫（ChromaDB/Qdrant），並原生整合 Google Gemini `text-embedding-004` 提供工業級的語義向量化能力。
- **Cross-Encoder Reranking**: 內建 SOTA 重排模型，對原始檢索結果進行二次精確排序，顯著提升最終內容的相關性分數。

### 3. 高穩定性非同步入庫管道 (Asynchronous ETL Pipeline)
文件入庫不再阻塞 API，而是透過背景自動化管道執行：
- **自動化歸檔**: 處理成功的檔案自動移動至 `processed/` 目錄，確保監控目錄清潔。
- **故障隔離與診斷**: 處理失敗的檔案會移動至 `error/`，並自動生成詳細的 `.log` 日誌檔，實現工業級的可追蹤性。
- **掃描機制**: 系統啟動即進行即時掃描 (Immediate Scan)，並支援自定義週期間隔掃描。

### 4. 現代化效能優化 (Modern Engineering)
- **uv 生態系**: 全線採用最新的 `uv` 作為套件管理器，環境建置與依賴解析速度比傳統 pip 快 10 倍以上。
- **Docker 快取優化**: 深度優化 Docker Layer Cache 與 UV 快取掛載，讓 CI/CD 流程中的映像檔構建極速完成。
- **Clean Architecture (CA)**: 程式碼嚴格遵守潔淨架構規範（Domain/Application/Infrastructure 分層）。這意味著更換向量資料庫或 LLM 模型僅需更動基礎設施層，極具未來擴展性。
- **Spec-Driven Development (OpenSpec)**: 核心功能的開發遵循 OpenSpec 規格驅動，確保「實作即規格」，系統行為 100% 可預期。
- **Observability**: 採用結構化 JSON 日誌與 `trace_id` 追蹤技術，開發者可在高併發環境下精準還原 Agent 的「思維鏈 (Thought Process)」。

---

## 🏗️ 技術棧摘要 (Technical Stack)
- **Core**: Python 3.11 / FastAPI
- **Retrieval**: ChromaDB & Qdrant (Switchable Vector) + Gemini Embeddings + BM25/Full-text + Cross-Encoder (Rerank)
- **Ingestion**: Docling / Unstructured / PyMuPDF (Multi-Parser)
- **Ops**: Docker Compose / uv / GPU + CPU Hybrid Deployment
