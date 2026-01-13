from typing import List, Optional
import logging

from advence_rag.domain.entities import SearchResult
from advence_rag.domain.interfaces import KnowledgeBaseRepository, RerankerService
from advence_rag.config import get_settings

logger = logging.getLogger("advence_rag")
settings = get_settings()

class HybridSearchUseCase:
    """Use case for performing hybrid search (Vector + BM25) and reranking."""
    
    def __init__(
        self, 
        kb_repo: KnowledgeBaseRepository, 
        reranker: RerankerService
    ):
        self.kb_repo = kb_repo
        self.reranker = reranker

    def execute(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Execute the hybrid search flow."""
        # 1. Parallel search (for now sequential but can be improved)
        # We fetch more results for the reranker to ensure better final top_k
        fetch_k = top_k * 3
        
        vector_results = self.kb_repo.search_similar(query, top_k=fetch_k)
        keyword_results = self.kb_repo.search_keyword(query, top_k=fetch_k)
        
        # 2. Merge and Deduplicate
        seen_ids = set()
        merged = []
        
        for res in vector_results + keyword_results:
            if res.id not in seen_ids:
                seen_ids.add(res.id)
                merged.append(res)
        
        if not merged:
            return []
            
        # 3. Rerank
        return self.reranker.rerank(query, merged, top_k=top_k)
