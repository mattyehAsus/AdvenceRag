"""RAG Pipeline - 檢索→審核→回答 流程。

提供兩種模式：
1. simple: Search → Review → Write（快速）
2. full: Planner → Search → LoopAgent(Review) → Write（完整）

透過 settings.rag_pipeline_mode 設定切換。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from advence_rag.agents.planner import planner_agent
from advence_rag.agents.reviewer import reviewer_agent
from advence_rag.agents.search import search_agent
from advence_rag.agents.writer import writer_agent
from advence_rag.config import get_settings

settings = get_settings()


def _recreate_agent(agent: Agent) -> Agent:
    """重建 agent 以避免 parent ownership 問題。"""
    return Agent(
        name=agent.name,
        model=agent.model,
        description=agent.description,
        instruction=agent.instruction,
        tools=agent.tools,
        output_key=getattr(agent, "output_key", None),
    )


# === 簡易版 Pipeline ===
# 流程：Search → Review → Write
rag_pipeline_simple = SequentialAgent(
    name="rag_pipeline_simple",
    description=(
        "簡易 RAG 管線：搜尋 → 審核 → 回答"
    ),
    sub_agents=[
        _recreate_agent(search_agent),
        _recreate_agent(reviewer_agent),
        _recreate_agent(writer_agent),
    ],
)


# === 完整版 Pipeline ===
# 流程：Planner → Search → LoopAgent(Review) → Write
rag_pipeline_full = SequentialAgent(
    name="rag_pipeline_full",
    description=(
        "完整 RAG 管線：問題分解 → 搜尋 → 迭代審核 → 回答"
    ),
    sub_agents=[
        _recreate_agent(planner_agent),   # 1. 問題分解
        _recreate_agent(search_agent),    # 2. 檢索資料
        LoopAgent(                         # 3. 迭代審核
            name="review_loop",
            description="迭代驗證檢索結果直到資訊充足",
            sub_agents=[_recreate_agent(reviewer_agent)],
            max_iterations=settings.max_reflection_iterations,
        ),
        _recreate_agent(writer_agent),    # 4. 生成回答
    ],
)


# === 根據設定選擇使用哪個 Pipeline ===
# 預設使用完整版，可透過 RAG_PIPELINE_MODE=simple 切換
_mode = getattr(settings, "rag_pipeline_mode", "full")
if _mode == "simple":
    rag_pipeline = rag_pipeline_simple
else:
    rag_pipeline = rag_pipeline_full
