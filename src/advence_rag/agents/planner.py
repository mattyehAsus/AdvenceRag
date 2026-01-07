"""Planner Agent - 問題分解與查詢規劃。

負責將複雜問題拆解為子問題，並生成結構化的查詢計劃。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


def decompose_query(query: str, context: str = "") -> dict[str, Any]:
    """將複雜查詢分解為子查詢。
    
    Args:
        query: 原始查詢
        context: 可選的上下文資訊
        
    Returns:
        dict: 包含子查詢列表和執行策略
    """
    # 此函數主要由 LLM 驅動，這裡提供基本結構
    return {
        "original_query": query,
        "context": context,
        "sub_queries": [],  # LLM 會填充這個
        "execution_strategy": "sequential",  # sequential | parallel
        "requires_aggregation": True,
    }


def create_search_plan(
    sub_queries: list[str],
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """建立檢索計劃。
    
    Args:
        sub_queries: 子查詢列表
        sources: 指定的資料來源
        
    Returns:
        dict: 檢索計劃
    """
    if sources is None:
        sources = ["knowledge_base"]
    
    return {
        "queries": sub_queries,
        "sources": sources,
        "retrieval_config": {
            "top_k": settings.retrieval_top_k,
            "use_rerank": True,
            "fallback_to_web": True,
        },
    }


# Planner Agent 定義
planner_agent = Agent(
    name="planner_agent",
    model=settings.llm_model,
    description=(
        "查詢規劃代理，負責分析複雜問題並將其分解為可執行的子查詢。"
        "產出結構化的檢索計劃供 Search Agent 執行。"
    ),
    instruction=(
        "你是一個查詢規劃專家。你的職責是：\n"
        "1. 分析使用者的複雜問題\n"
        "2. 將問題分解為 2-5 個獨立的子問題\n"
        "3. 決定子問題的執行順序（順序或並行）\n"
        "4. 為每個子問題指定最適合的資料來源\n\n"
        "分解原則：\n"
        "- 每個子問題應該是獨立可回答的\n"
        "- 子問題應該涵蓋原問題的所有面向\n"
        "- 避免重複或過度分解\n\n"
        "使用 decompose_query 和 create_search_plan 工具。"
    ),
    tools=[decompose_query, create_search_plan],
    output_key="search_plan",  # 將輸出存入 state
)
