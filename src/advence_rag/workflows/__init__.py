"""Workflows module - 工作流程定義。"""

from advence_rag.workflows.rag_pipeline import get_rag_pipeline
from advence_rag.workflows.optimization import optimization_pipeline

def __getattr__(name):
    if name == "rag_pipeline":
        return get_rag_pipeline()
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["get_rag_pipeline", "optimization_pipeline", "rag_pipeline"]
