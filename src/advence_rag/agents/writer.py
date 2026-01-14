"""Writer Agent - 回答生成。

負責基於驗證過的資料生成最終回答，並注入引用和來源資訊。
"""

from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


def generate_answer_with_citations(
    query: str,
    verified_docs: list[dict[str, Any]],
    style: str = "comprehensive",
) -> dict[str, Any]:
    """生成帶有引用的回答。
    
    Args:
        query: 使用者查詢
        verified_docs: 經過驗證的文檔
        style: 回答風格 (comprehensive | concise | technical)
        
    Returns:
        dict: 生成的回答和引用資訊
    """
    return {
        "answer": "",  # LLM 生成
        "citations": [],
        "confidence": 0.0,
        "style": style,
    }


def format_sources(docs: list[dict[str, Any]]) -> list[dict[str, str]]:
    """格式化來源資訊供引用使用。
    
    Args:
        docs: 文檔列表
        
    Returns:
        list: 格式化的來源列表
    """
    sources = []
    for idx, doc in enumerate(docs, 1):
        sources.append({
            "id": f"[{idx}]",
            "title": doc.get("title", "Unknown"),
            "source": doc.get("source", "knowledge_base"),
            "url": doc.get("url", ""),
        })
    return sources


def add_disclaimer_if_needed(
    answer: str,
    confidence: float,
    has_web_sources: bool,
) -> str:
    """根據信心度和來源類型添加免責聲明。
    
    Args:
        answer: 原始回答
        confidence: 信心分數
        has_web_sources: 是否包含網路來源
        
    Returns:
        str: 可能附加免責聲明的回答
    """
    disclaimers = []
    
    if confidence < 0.7:
        disclaimers.append("⚠️ 此回答的信心度較低，建議進一步驗證。")
    
    if has_web_sources:
        disclaimers.append("ℹ️ 部分資訊來自網路搜索，請注意時效性。")
    
    if disclaimers:
        return answer + "\n\n---\n" + "\n".join(disclaimers)
    
    return answer


# Writer Agent 定義
writer_agent = Agent(
    name="writer_agent",
    model=settings.llm_model,
    description=(
        "回答生成代理，負責基於經過驗證的資訊生成高品質、"
        "有引用的最終回答。"
    ),
    instruction=(
        "你是一個專業的技術寫作專家。你的職責是：\n"
        "1. 根據經過 Reviewer 驗證的資料生成回答\n"
        "2. 確保回答直接回應使用者問題\n"
        "3. **不要使用任何工具**，直接輸出 Markdown 格式的回答\n"
        "4. **當涉及比較時，務必使用 Markdown 表格展示**\n"
        "5. 為每個重要陳述添加引用 [1], [2] 等\n"
        "6. 在回答末尾列出所有參考來源（**必須使用 search_results 中提供的 Title/Source，禁止使用 'unknown'**）\n\n"
        "寫作原則：\n"
        "- 準確性優先：只陳述有來源支持的資訊\n"
        "- 結構清晰：使用標題、列表、程式碼區塊等\n"
        "- **數據視覺化：比較型資訊優先使用表格**\n"
        "- 適當長度：全面但不冗長\n"
        "- 誠實謙遜：對不確定的部分明確說明\n\n"
        "直接開始你的回答，不要解釋你要做什麼。"
    ),
    tools=[],  # 移除所有工具，強制直接輸出文字
    output_key="final_answer",
)
