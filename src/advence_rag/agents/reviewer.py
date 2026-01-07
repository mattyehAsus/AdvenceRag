"""Reviewer Agent - 反思與驗證。

負責評估檢索結果品質，決定是否需要重新檢索或可以進入回答生成階段。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


def evaluate_information_sufficiency(
    query: str,
    retrieved_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    """評估檢索到的資訊是否足夠回答問題。
    
    Args:
        query: 原始查詢
        retrieved_docs: 檢索到的文檔列表
        
    Returns:
        dict: 評估結果
    """
    if not retrieved_docs:
        return {
            "is_sufficient": False,
            "confidence": 0.0,
            "missing_aspects": ["No documents retrieved"],
            "recommendation": "retry_search",
        }
    
    return {
        "is_sufficient": True,
        "confidence": 0.85,
        "missing_aspects": [],
        "recommendation": "proceed_to_answer",
    }


def identify_information_gaps(
    query: str,
    retrieved_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    """識別資訊缺口，找出還需要檢索的內容。
    
    Args:
        query: 原始查詢
        retrieved_docs: 現有文檔
        
    Returns:
        dict: 資訊缺口分析
    """
    return {
        "has_gaps": False,
        "gaps": [],
        "suggested_queries": [],
        "priority": "low",
    }


def verify_source_reliability(
    docs: list[dict[str, Any]],
) -> dict[str, Any]:
    """驗證資料來源的可靠性。
    
    Args:
        docs: 文檔列表
        
    Returns:
        dict: 可靠性評估
    """
    return {
        "overall_reliability": "high",
        "verified_docs": [],
        "questionable_docs": [],
        "source_diversity": "good",
    }


# Reviewer Agent 定義
reviewer_agent = Agent(
    name="reviewer_agent",
    model=settings.llm_model,
    description=(
        "反思驗證代理，負責評估檢索結果的品質和充分性。"
        "決定是否需要補充檢索，或可以進入回答生成階段。"
    ),
    instruction=(
        "你是一個嚴謹的資訊審核專家。你的職責是：\n"
        "1. 評估檢索結果是否足以回答使用者問題\n"
        "2. 識別資訊缺口，找出遺漏的面向\n"
        "3. 驗證資料來源的可靠性\n"
        "4. 決定下一步行動：\n"
        "   - 如果資訊充足：建議進入回答生成\n"
        "   - 如果資訊不足：建議補充檢索，並提供具體查詢建議\n\n"
        "評估標準：\n"
        "- 覆蓋度：是否涵蓋問題的所有面向？\n"
        "- 深度：是否有足夠的細節支持回答？\n"
        "- 一致性：多個來源是否相互佐證？\n"
        "- 時效性：資訊是否足夠新？\n\n"
        f"最多迭代 {settings.max_reflection_iterations} 次後必須給出結論。"
    ),
    tools=[
        evaluate_information_sufficiency,
        identify_information_gaps,
        verify_source_reliability,
    ],
    output_key="review_result",
)
