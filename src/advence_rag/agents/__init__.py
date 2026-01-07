"""Agent definitions module."""

import sys
from pathlib import Path

# 確保 src 目錄在 sys.path 中，以支援絕對導入
# ADK 直接載入此模組，所以需要在這裡設定路徑
_src_path = Path(__file__).resolve().parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from advence_rag.agents.guard import guard_agent
from advence_rag.agents.orchestrator import orchestrator_agent
from advence_rag.agents.planner import planner_agent
from advence_rag.agents.reviewer import reviewer_agent
from advence_rag.agents.search import search_agent
from advence_rag.agents.writer import writer_agent

__all__ = [
    "guard_agent",
    "orchestrator_agent",
    "planner_agent",
    "search_agent",
    "reviewer_agent",
    "writer_agent",
]
