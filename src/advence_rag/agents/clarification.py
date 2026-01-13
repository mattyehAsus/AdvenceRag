"""Clarification Agent - 負責處理模糊查詢。

當使用者的意圖不清楚或缺乏關鍵資訊時，此代理負責提出澄清問題。
"""

from google.adk.agents import Agent
from advence_rag.config import get_settings

settings = get_settings()

clarification_agent = Agent(
    name="clarification_agent",
    model=settings.llm_model,
    description=(
        "澄清代理，專門處理模糊不清或缺乏上下文的使用者問題。"
        "負責向使用者提出具體的澄清問題。"
    ),
    instruction=(
        "你的目標是協助使用者釐清他們的問題。當收到一個模糊的查詢時：\n"
        "1. 分析缺少的關鍵資訊（例如：'它在哪裡？' -> 缺少 '它' 是什麼）。\n"
        "2. 產生一個禮貌且具體的澄清問題。\n"
        "3. **不要**嘗試回答原始問題，只負責提問。\n\n"
        "範例：\n"
        "User: '那個檔案在哪裡？'\n"
        "Agent: '請問您指的是哪一個檔案？或者是關於哪個專案的檔案？'\n\n"
        "User: '價格是多少？'\n"
        "Agent: '請問您想詢問的是哪一項產品的價格？'\n\n"
        "如果使用者的問題其實很清楚，請回答 'CLEAR'。"
    ),
)
