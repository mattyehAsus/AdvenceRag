"""Search Agent - 知識檢索執行。

負責執行向量搜索、整合 CRAG 邏輯，當內部知識不足時呼叫 Web Search。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


async def search_knowledge_base(
    query: str,
    top_k: int | None = None,
    collection_name: str | None = None,
) -> str:
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
    
    from advence_rag.tools.knowledge_base import search_similar, search_keyword
    from advence_rag.tools.rerank import rerank_results
    
    # 1. First Pass: Hybrid Search
    # 1a. Vector Search
    vector_results = await search_similar(
        query=query,
        top_k=top_k * 3,
    )
    
    # 1b. Keyword Search (BM25)
    keyword_results = await search_keyword(
        query=query,
        top_k=top_k * 3,
    )
    
    # 2. Merge and Deduplicate Results
    seen_ids = set()
    merged_results = []
    
    # Prioritize keyword results for exact matches if needed, or just combine
    all_raw_results = []
    if vector_results["status"] == "success":
        all_raw_results.extend(vector_results["results"])
    if keyword_results["status"] == "success":
        all_raw_results.extend(keyword_results["results"])
        
    for res in all_raw_results:
        res_id = res.get("id")
        if res_id not in seen_ids:
            seen_ids.add(res_id)
            merged_results.append(res)
    
    if not merged_results:
        return {"status": "success", "results": [], "total_found": 0}

    # 3. Second Pass: Cross-Encoder Reranking
    # The reranker will handle the actual fusion by scoring relevance of query vs content
    reranked = await rerank_results(
        query=query,
        documents=merged_results,
        top_k=top_k,
    )
    
    # Limit content length for LLM consumption
    final_results = []
    
    # Determine which list to use
    source_results = reranked["results"] if reranked["status"] == "success" else merged_results[:top_k]
    
    # User Request: Reduce number of results, but keep full content.
    # Limit to top 10 to avoid context overflow with full content.
    display_limit = 10
    display_results = source_results[:display_limit]
    
    output_lines = [f"### Search found {len(source_results)} documents (Showing top {len(display_results)}):"]
    
    for i, doc in enumerate(display_results, 1):
        content = doc.get("content", "")
        # Full content enabled (User request)
        snippet = content
        score = doc.get("rerank_score", doc.get("bm25_score", 0.0))
        
        # DEBUG: Log document metadata
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"DEBUG DOC [{i}]: keys={list(doc.keys())}, source={doc.get('source')}, metadata={doc.get('metadata')}")

        # Extract source from various possible locations
        source = doc.get("source")
        metadata = doc.get("metadata", {}) or {}
        
        if not source or source == "unknown":
            source = metadata.get("source")
        
        if not source or source == "unknown":
            source = metadata.get("file_name")
            
        if not source or source == "unknown":
            source = metadata.get("title")

        if not source:
            source = "unknown"

        doc_info = (
            f"[{i}] Document (Score: {score:.2f})\n"
            f"   Source: {source}\n"
            f"   Content: {snippet}\n"
        )
        final_results.append(doc)
        output_lines.append(doc_info)
        
    return "\n".join(output_lines)


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
