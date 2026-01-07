"""Processing Workflow - 處理團隊流程。

流程：Reviewer ↔ Writer（迭代驗證）
使用 LoopAgent 實現迭代直到資訊充足。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from advence_rag.agents.reviewer import reviewer_agent
from advence_rag.agents.writer import writer_agent
from advence_rag.config import get_settings

settings = get_settings()


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


# Processing Team: 驗證 → 生成（可迭代）
processing_flow = SequentialAgent(
    name="processing_team",
    description=(
        "處理團隊，負責驗證檢索結果品質並生成最終回答。"
        "如果資訊不足會請求補充檢索。"
    ),
    sub_agents=[
        # Reviewer 可能需要迭代驗證
        LoopAgent(
            name="review_loop",
            description="迭代驗證檢索結果直到資訊充足",
            sub_agents=[_recreate_agent(reviewer_agent)],
            max_iterations=settings.max_reflection_iterations,
        ),
        # 驗證通過後生成回答
        _recreate_agent(writer_agent),
    ],
)
