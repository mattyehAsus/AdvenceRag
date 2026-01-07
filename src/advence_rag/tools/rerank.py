"""Rerank Tool - 使用 Cross-Encoder 重新排序檢索結果。"""

from typing import Any

from advence_rag.config import get_settings

settings = get_settings()

# Lazy-loaded reranker
_reranker = None


def _get_reranker():
    """Get or create the reranker model (lazy initialization)."""
    global _reranker
    
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(settings.rerank_model)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for reranking. "
                "Install with: pip install sentence-transformers"
            )
    
    return _reranker


def rerank_results(
    query: str,
    documents: list[dict[str, Any]],
    top_k: int | None = None,
) -> dict[str, Any]:
    """使用 Cross-Encoder 重新排序檢索結果。
    
    Args:
        query: 原始查詢
        documents: 要重排序的文檔列表，每個文檔需有 'content' 欄位
        top_k: 返回的結果數量
        
    Returns:
        dict: 重排序後的結果
    """
    if top_k is None:
        top_k = settings.rerank_top_k
    
    if not documents:
        return {
            "status": "success",
            "results": [],
            "original_count": 0,
            "reranked_count": 0,
        }
    
    try:
        reranker = _get_reranker()
        
        # 準備 query-document pairs
        pairs = [(query, doc.get("content", "")) for doc in documents]
        
        # 計算相關性分數
        scores = reranker.predict(pairs)
        
        # 將分數加入文檔並排序
        scored_docs = []
        for doc, score in zip(documents, scores):
            doc_with_score = doc.copy()
            doc_with_score["rerank_score"] = float(score)
            scored_docs.append(doc_with_score)
        
        # 按分數降序排序
        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # 取前 top_k 個
        top_results = scored_docs[:top_k]
        
        return {
            "status": "success",
            "results": top_results,
            "original_count": len(documents),
            "reranked_count": len(top_results),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "results": documents[:top_k],  # Fallback to original order
            "original_count": len(documents),
            "reranked_count": 0,
        }
