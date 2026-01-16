"""RAG Pipeline - 檢索→審核→回答 流程。

提供兩種模式：
1. simple: Search → Review → Write（快速）
2. full: Planner → Search → LoopAgent(Review) → Write（完整）

透過 settings.rag_pipeline_mode 設定切換。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from advence_rag.config import get_settings

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

def get_rag_pipeline() -> SequentialAgent:
    """獲取配置好的 RAG Pipeline 實例（延遲載入以避免循環導入）。"""
    settings = get_settings()
    
    # 延遲導入 agents 以打破循環依賴
    # rag_pipeline -> agents -> orchestrator -> rag_pipeline
    from advence_rag.agents.planner import planner_agent
    from advence_rag.agents.reviewer import reviewer_agent
    from advence_rag.agents.search import search_agent
    from advence_rag.agents.writer import writer_agent

    # === 簡易版 Pipeline ===
    rag_pipeline_simple = SequentialAgent(
        name="rag_pipeline_simple",
        description="簡易 RAG 管線：搜尋 → 審核 → 回答",
        sub_agents=[
            _recreate_agent(search_agent),
            _recreate_agent(reviewer_agent),
            _recreate_agent(writer_agent),
        ],
    )

    # === 完整版 Pipeline ===
    rag_pipeline_full = SequentialAgent(
        name="rag_pipeline_full",
        description="完整 RAG 管線：問題分解 → 搜尋 → 迭代審核 → 回答",
        sub_agents=[
            _recreate_agent(planner_agent),
            _recreate_agent(search_agent),
            LoopAgent(
                name="review_loop",
                description="迭代驗證檢索結果直到資訊充足",
                sub_agents=[_recreate_agent(reviewer_agent)],
                max_iterations=settings.max_reflection_iterations,
            ),
            _recreate_agent(writer_agent),
        ],
    )

    _mode = getattr(settings, "rag_pipeline_mode", "full")
    if _mode == "simple":
        return rag_pipeline_simple
    return rag_pipeline_full

# 為相容性保留全域變數（由 orchestrator 呼叫 get_rag_pipeline 後賦值或直接使用）
# 注意：在模組層級直接賦值仍會觸發導入，所以我們在 orchestrator 中動態獲取
