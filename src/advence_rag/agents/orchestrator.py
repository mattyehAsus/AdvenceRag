"""Orchestrator Agent - 總協調者/Router。

負責根據問題類型分派給適當的子 agent，管理整體對話流程。
"""

from google.adk.agents import Agent

from advence_rag.agents.clarification import clarification_agent
from advence_rag.agents.planner import planner_agent
from advence_rag.config import get_settings
from advence_rag.workflows.rag_pipeline import get_rag_pipeline

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
        "1. **理解使用者意圖**：分析使用者問題的類型\n"
        "2. **路由決策**：\n"
        "   - **語意模糊/缺乏上下文**（如 '它在哪裡？', '價格多少？'）：交給 clarification_agent 提問\n"
        "   - **簡單問候**（如 hello, hi）：**直接由你自己回應**。**不要呼叫任何子代理**。\n"
        "   - **知識問題**：交給 rag_pipeline，它會自動執行 檢索→審核→回答 的完整流程\n"
        "   - **複雜問題需要分解**：先用 planner_agent 分解，再交給 rag_pipeline\n\n"
        f"**重要限制**：最多進行 {settings.max_agent_iterations} 次代理間轉移。\n\n"
        "範例：\n"
        "- User: Hello → 你直接回應\n"
        "- User: 它在哪裡？ → clarification_agent\n"
        "- User: 豐收款API是什麼 → rag_pipeline（會自動完成完整流程）"
    ),
    sub_agents=[
        clarification_agent,
        planner_agent,
        get_rag_pipeline(),  # 動態獲取 SequentialAgent，避免循環導入
    ],
)
