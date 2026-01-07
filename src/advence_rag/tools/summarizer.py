"""Summarizer Tool - 文檔摘要生成。"""

from typing import Any

from google import genai

from advence_rag.config import get_settings

settings = get_settings()


def summarize_document(
    content: str,
    max_length: int = 500,
    style: str = "concise",
) -> dict[str, Any]:
    """生成文檔摘要。
    
    Args:
        content: 要摘要的文檔內容
        max_length: 摘要最大長度（字數）
        style: 摘要風格 (concise | detailed | bullet_points)
        
    Returns:
        dict: 摘要結果
    """
    if not content.strip():
        return {
            "status": "error",
            "error": "Empty content provided",
            "summary": "",
        }
    
    style_instructions = {
        "concise": "提供簡潔的摘要，突出關鍵要點。",
        "detailed": "提供詳細的摘要，保留重要細節。",
        "bullet_points": "使用條列式摘要主要觀點。",
    }
    
    instruction = style_instructions.get(style, style_instructions["concise"])
    
    prompt = f"""請為以下文檔生成摘要。

要求：
- {instruction}
- 長度控制在 {max_length} 字以內
- 保持客觀準確
- 使用繁體中文

文檔內容：
{content}

摘要："""

    try:
        client = genai.Client(api_key=settings.google_api_key)
        response = client.models.generate_content(
            model=settings.llm_model,
            contents=prompt,
        )
        
        summary = response.text.strip()
        
        return {
            "status": "success",
            "summary": summary,
            "style": style,
            "original_length": len(content),
            "summary_length": len(summary),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "summary": "",
        }


def extract_key_points(content: str, max_points: int = 5) -> dict[str, Any]:
    """從文檔中提取關鍵要點。
    
    Args:
        content: 文檔內容
        max_points: 最大要點數量
        
    Returns:
        dict: 關鍵要點列表
    """
    if not content.strip():
        return {
            "status": "error",
            "error": "Empty content provided",
            "key_points": [],
        }
    
    prompt = f"""請從以下文檔中提取最重要的 {max_points} 個關鍵要點。

要求：
- 每個要點一行
- 使用簡潔的陳述
- 按重要性排序
- 使用繁體中文

文檔內容：
{content}

關鍵要點："""

    try:
        client = genai.Client(api_key=settings.google_api_key)
        response = client.models.generate_content(
            model=settings.llm_model,
            contents=prompt,
        )
        
        # 解析要點
        text = response.text.strip()
        points = [
            line.strip().lstrip("•-123456789. ")
            for line in text.split("\n")
            if line.strip()
        ][:max_points]
        
        return {
            "status": "success",
            "key_points": points,
            "count": len(points),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "key_points": [],
        }
