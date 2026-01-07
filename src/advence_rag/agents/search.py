"""Search Agent - 知識檢索執行。

負責執行向量搜索、整合 CRAG 邏輯，當內部知識不足時呼叫 Web Search。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


def search_knowledge_base(
    query: str,
    top_k: int | None = None,
    collection_name: str | None = None,
) -> dict[str, Any]:
    """從知識庫檢索相關文檔。
    
    Args:
        query: 查詢文字
        top_k: 返回結果數量
        collection_name: Chroma collection 名稱
        
    Returns:
        dict: 檢索結果
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    # Import here to avoid circular dependencies if any, 
    # though tools is a lower layer so it should be fine.
    from advence_rag.tools.knowledge_base import search_similar
    from advence_rag.tools.rerank import rerank_results
    
    # 1. First Pass: Vector Search (Retrieve more candidates for reranking)
    # We retrieve 2x or 3x top_k to let reranker select the best
    initial_results = search_similar(
        query=query,
        top_k=top_k * 3,
    )
    
    if initial_results["status"] != "success" or not initial_results["results"]:
        return initial_results

    # 2. Second Pass: Cross-Encoder Reranking
    reranked = rerank_results(
        query=query,
        documents=initial_results["results"],
        top_k=top_k,
    )
    
    if reranked["status"] == "success":
        return {
            "status": "success",
            "query": query,
            "results": reranked["results"],
            "total_found": initial_results["total_found"],
            "reranked": True
        }
    
    return initial_results


def search_web(query: str, num_results: int = 5) -> dict[str, Any]:
    """使用 Google Search 進行網路搜索 (CRAG fallback)。
    
    Args:
        query: 搜索查詢
        num_results: 返回結果數量
        
    Returns:
        dict: 搜索結果
    """
    from advence_rag.tools.web_search import search_google
    
    return search_google(query, num_results)


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
        "5. 整合並返回最相關的文檔\n\n"
        "CRAG 策略：\n"
        "- 評估每個檢索結果的相關性分數\n"
        "- 如果平均分數 < 0.7 或結果數量 < 3，觸發網路搜索\n"
        "- 合併知識庫和網路結果，去重後返回\n\n"
        "使用 search_knowledge_base, search_web, evaluate_retrieval_quality 工具。"
    ),
    tools=[search_knowledge_base, search_web, evaluate_retrieval_quality],
    output_key="search_results",
)
