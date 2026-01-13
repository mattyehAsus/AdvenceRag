from typing import List, Optional
from advence_rag.domain.entities import SearchResult
from advence_rag.domain.interfaces import RerankerService
from advence_rag.tools.rerank import rerank_results

class CrossEncoderReranker(RerankerService):
    """Infrastructure implementation of RerankerService using Sentence-Transformers."""
    
    def rerank(self, query: str, documents: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        if not documents:
            return []
            
        # Convert Domain SearchResult back to tool-compatible dicts
        raw_docs = [
            {
                "content": doc.content,
                "metadata": doc.metadata,
                "id": doc.id,
            } for doc in documents
        ]
        
        res = rerank_results(query, raw_docs, top_k=top_k)
        
        if res["status"] != "success":
            return documents[:top_k]
            
        return [
            SearchResult(
                content=r["content"],
                metadata=r["metadata"],
                id=r["id"],
                score=r["rerank_score"]
            ) for r in res["results"]
        ]
