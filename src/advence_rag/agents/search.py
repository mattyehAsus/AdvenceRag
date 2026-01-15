"""Search Agent - 知識檢索執行。

負責執行向量搜索、整合 CRAG 邏輯，當內部知識不足時呼叫 Web Search。
現在使用 HybridSearchUseCase 進行核心搜尋邏輯。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()

# Lazy-loaded use case instance
_search_use_case = None


def _get_search_use_case():
    """Get or create the HybridSearchUseCase instance (lazy initialization)."""
    global _search_use_case
    
    if _search_use_case is None:
        from advence_rag.application.use_cases.search import HybridSearchUseCase
        from advence_rag.infrastructure.persistence.hybrid_repository import HybridKnowledgeBaseRepository
        from advence_rag.infrastructure.ai.reranker_service import CrossEncoderReranker
        from advence_rag.infrastructure.ai.web_search_service import SerperWebSearchService
        
        kb_repo = HybridKnowledgeBaseRepository()
        reranker = CrossEncoderReranker()
        web_search = SerperWebSearchService()
        
        _search_use_case = HybridSearchUseCase(
            kb_repo=kb_repo,
            reranker=reranker,
            web_search=web_search,
        )
    
    return _search_use_case


async def search_knowledge_base(
    query: str,
    top_k: int | None = None,
    collection_name: str | None = None,
) -> str:
    """從知識庫檢索相關文檔（使用 HybridSearchUseCase）。
    
    Args:
        query: 查詢文字
        top_k: 返回結果數量
        collection_name: Chroma collection 名稱 (目前未使用)
        
    Returns:
        str: 格式化的檢索結果，供 LLM 閱讀
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    use_case = _get_search_use_case()
    
    # Execute hybrid search with CRAG
    results = await use_case.execute(query, top_k=top_k)
    
    # Format results for LLM consumption
    return use_case.format_for_llm(query, results)


async def search_web(query: str, num_results: int = 5) -> dict[str, Any]:
    """使用配置的搜尋引擎 (Serper/Google) 進行網路搜索 (CRAG fallback)。
    
    具備自動智慧備援功能：如果優先搜尋引擎失敗，會自動切換至另一個引擎。

    Args:
        query: 搜索查詢
        num_results: 返回結果數量
        
    Returns:
        dict: 搜索結果
    """
    from advence_rag.tools.web_search import search_web as tool_search_web
    
    return await tool_search_web(query, num_results)


def evaluate_retrieval_quality(
    query: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """評估檢索結果品質，決定是否需要 CRAG fallback。
    
    Args:
        query: 原始查詢
        results: 檢索結果列表
        
    Returns:
        dict: 品質評估結果
    """
    if not results:
        return {
            "quality": "poor",
            "score": 0.0,
            "needs_web_search": True,
            "reason": "No results found in knowledge base",
        }
    
    # Check top-1 score
    # Cross-Encoder scores are usually logits. 
    # > 0 usually implies relevant for models trained with BCE (like ms-marco).
    top_score = results[0].get("rerank_score", -999.0)
    
    # Threshold can be tuned. 0.0 is a reasonable starting point for relevant/non-relevant.
    threshold = 0.0 
    
    if top_score < threshold:
         return {
            "quality": "poor",
            "score": top_score,
            "needs_web_search": True,
            "reason": f"Top result score ({top_score:.2f}) below threshold ({threshold})",
        }

    return {
        "quality": "good",
        "score": top_score,
        "needs_web_search": False,
        "reason": "Sufficient results from knowledge base",
    }


# Search Agent 定義
search_agent = Agent(
    name="search_agent",
    model=settings.llm_model,
    description=(
        "檢索代理，負責從知識庫和網路搜索相關資訊。"
        "實作 CRAG (Corrective RAG) 邏輯，當知識庫資料不足時自動切換到網路搜索。"
    ),
    instruction=(
        "你是一個檢索專家。你的職責是：\n"
        "1. 根據 Planner 提供的查詢計劃執行檢索\n"
        "2. 首先從內部知識庫 (Chroma) 檢索\n"
        "3. 評估檢索結果的品質和相關性\n"
        "4. 如果結果不足，使用 CRAG 策略進行網路搜索補充\n"
        "5. **CRITICAL STEP**: After tools execution, you **MUST** speak!\n"
        "   - **Do NOT be silent.**\n"
        "   - You must output a detailed summary of what you found.\n"
        "   - Format: '### Search Results for [Query]...'\n"
        "   - Summarize the key content from the retrieved documents.\n"
        "   - **IMPORTANT**: You MUST list the reference source for each document found.\n"
        "     Example format:\n"
        "     - **[1] Title/Source**: Key content summary...\n"
        "     - **[2] Title/Source**: Key content summary...\n\n"
        "6. **MANDATORY HANDOFF**: 完成檢索摘要後，你必須明確表示：\n"
        "   '>>> 檢索完成，請交由 Reviewer 審核資料充分性。'\n"
        "   這將觸發 orchestrator 將結果傳遞給 reviewer_agent 進行品質審核。\n\n"
        "CRAG 策略：\n"
        "- 評估每個檢索結果的相關性分數\n"
        "- 如果平均分數 < 0.7 或結果數量 < 3，觸發網路搜索\n"
        "- 合併知識庫和網路結果，去重後返回\n\n"
        "使用 search_knowledge_base, search_web, evaluate_retrieval_quality 工具。"
    ),
    tools=[search_knowledge_base, search_web, evaluate_retrieval_quality],
    output_key="search_results",
)
