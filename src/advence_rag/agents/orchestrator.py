"""Orchestrator Agent - 總協調者/Router。

負責根據問題類型分派給適當的子 agent，管理整體對話流程。
"""

from google.adk.agents import Agent

from advence_rag.agents.planner import planner_agent
from advence_rag.agents.reviewer import reviewer_agent
from advence_rag.agents.search import search_agent
from advence_rag.agents.writer import writer_agent
from advence_rag.config import get_settings

settings = get_settings()


# Orchestrator Agent 定義
orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=settings.llm_model,
    description=(
        "總協調代理，負責理解使用者意圖並協調各個專門代理完成任務。"
        "作為系統的中央路由器，決定何時呼叫哪個子代理。"
    ),
    instruction=(
        "你是 RAG 系統的總協調者。你的職責是：\n\n"
        "1. **理解使用者意圖**：分析使用者問題的類型和複雜度\n"
        "2. **路由決策**：\n"
        "   - 簡單問題：直接使用 search_agent 檢索後交給 writer_agent\n"
        "   - 簡單問候（如 hello, hi）：直接交給 writer_agent 回應，**不需要 Search**\n"
        "   - 複雜問題：先用 planner_agent 分解，再執行檢索\n"
        "3. **流程控制**：\n"
        "   - 檢索結果必須經過 Reviewer Agent 審核\n"
        "   - 審核通過後交給 Writer Agent 生成回答\n"
        "4. **迭代處理**：如果 Reviewer 認為資訊不足，\n"
        "   協調 Search Agent 進行補充檢索\n\n"
        f"**重要限制**：最多進行 {settings.max_agent_iterations} 次代理間轉移。\n\n"
        "正確範例：\n"
        "User: Hello -> Orchestrator calls Writer -> Writer says 'Hello!'\n\n"
        "始終保持對話流暢，並在適當時候總結進度。"
    ),
    sub_agents=[
        planner_agent,
        search_agent,
        reviewer_agent,
        writer_agent,
    ],
)
