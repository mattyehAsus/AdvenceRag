"""Guard Agent - 敏感資料過濾與安全檢查。

負責檢查輸入/輸出是否包含敏感資訊，並決定是否允許繼續處理。
"""

import re
from typing import Any

from google.adk.agents import Agent

from advence_rag.config import get_settings

settings = get_settings()


def check_sensitive_content(text: str) -> dict[str, Any]:
    """檢查文字是否包含敏感內容。
    
    Args:
        text: 要檢查的文字內容
        
    Returns:
        dict: 包含 is_safe, reason, filtered_text 的結果
    """
    if not settings.guard_enabled:
        return {
            "is_safe": True,
            "reason": "Guard is disabled",
            "filtered_text": text,
        }
    
    # 預設敏感模式
    default_patterns = [
        r"\b\d{3}-?\d{2}-?\d{4}\b",  # SSN pattern
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
        r"\b[A-Z][12]\d{8}\b",  # Taiwan ID number
    ]
    
    # 合併使用者自定義模式
    all_patterns = default_patterns + settings.guard_sensitive_patterns
    
    for pattern in all_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "is_safe": False,
                "reason": f"Detected sensitive pattern: {pattern}",
                "filtered_text": None,
            }
    
    return {
        "is_safe": True,
        "reason": "No sensitive content detected",
        "filtered_text": text,
    }


def validate_query(query: str) -> dict[str, Any]:
    """驗證使用者查詢是否安全。
    
    Args:
        query: 使用者的查詢文字
        
    Returns:
        dict: 驗證結果
    """
    result = check_sensitive_content(query)
    
    if not result["is_safe"]:
        return {
            "status": "rejected",
            "message": "您的查詢包含敏感資訊，無法處理。",
            "can_proceed": False,
        }
    
    return {
        "status": "approved",
        "message": "查詢已通過安全檢查。",
        "can_proceed": True,
        "validated_query": query,
    }


# Guard Agent 定義
guard_agent = Agent(
    name="guard_agent",
    model=settings.llm_model,
    description=(
        "安全守衛代理，負責檢查使用者輸入是否包含敏感資訊，"
        "並過濾不當內容。在處理任何查詢前必須先通過此代理驗證。"
    ),
    instruction=(
        "你是一個安全守衛代理。你的職責是：\n"
        "1. 檢查使用者輸入是否包含敏感個人資訊（如身分證號、信用卡號等）\n"
        "2. 檢查是否有惡意意圖或不當請求\n"
        "3. 如果發現問題，禮貌地拒絕並說明原因\n"
        "4. 如果檢查通過，允許請求繼續處理\n\n"
        "使用 validate_query 工具來驗證查詢。"
    ),
    tools=[validate_query, check_sensitive_content],
)
