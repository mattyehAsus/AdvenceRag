"""ADK Agent Entry Point - root_agent 定義。

這是 ADK 的入口點，定義完整的 Multi-Agent 系統。
使用 `adk web src/advence_rag` 啟動開發伺服器。
"""

import sys
from pathlib import Path

# 確保 src 目錄在 sys.path 中，以支援絕對導入
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from google.adk.agents import SequentialAgent

from advence_rag.agents.guard import guard_agent
from advence_rag.agents.orchestrator import orchestrator_agent
from advence_rag.config import get_settings
from advence_rag.utils import setup_logging

# 初始化
settings = get_settings()
setup_logging(settings.log_level)


# Root Agent 定義
# 流程：Guard → Orchestrator（內含完整的 Retrieval + Processing 子系統）
root_agent = SequentialAgent(
    name="advence_rag",
    description=(
        "Advence RAG 多代理系統。\n"
        "結合安全過濾、智慧路由、知識檢索、反思驗證等能力，"
        "提供高品質的 RAG 問答服務。"
    ),
    sub_agents=[
        orchestrator_agent,  # 智慧協調（內含 Guard, Retrieval, Processing 等子系統）
    ],
)


# 導出 root_agent（ADK 會自動尋找此變數）
__all__ = ["root_agent"]
