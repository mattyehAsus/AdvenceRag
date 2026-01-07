"""Retrieval Workflow - 檢索團隊流程。

流程：Planner → Search → Rerank
使用 SequentialAgent 串接執行。
"""

from google.adk.agents import Agent, SequentialAgent

from advence_rag.agents.planner import planner_agent
from advence_rag.agents.search import search_agent


def _recreate_agent(agent: Agent) -> Agent:
    """Manually recreate an agent to avoid parent ownership issues."""
    return Agent(
        name=agent.name,
        model=agent.model,
        description=agent.description,
        instruction=agent.instruction,
        tools=agent.tools,
        output_key=getattr(agent, "output_key", None),
    )


# Retrieval Team: 順序執行 Planner → Search
# Rerank 是作為 tool 整合在 search pipeline 中
retrieval_flow = SequentialAgent(
    name="retrieval_team",
    description=(
        "檢索團隊，負責將複雜問題分解後執行檢索。"
        "流程：問題分解 → 向量檢索 → (CRAG fallback) → 重排序"
    ),
    sub_agents=[
        _recreate_agent(planner_agent),
        _recreate_agent(search_agent),
    ],
)
