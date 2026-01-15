"""Hybrid Search Use Case with CRAG support."""

from typing import List, Optional
import logging

from advence_rag.domain.entities import SearchResult
from advence_rag.domain.interfaces import (
    KnowledgeBaseRepository, 
    RerankerService, 
    WebSearchService,
)
from advence_rag.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# CRAG Quality Threshold: Cross-Encoder scores > 0 usually indicate relevance
CRAG_QUALITY_THRESHOLD = 0.0


class HybridSearchUseCase:
    """Use case for performing hybrid search (Vector + BM25), reranking, and optional CRAG fallback."""
    
    def __init__(
        self, 
        kb_repo: KnowledgeBaseRepository, 
        reranker: RerankerService,
        web_search: Optional[WebSearchService] = None,
    ):
        self.kb_repo = kb_repo
        self.reranker = reranker
        self.web_search = web_search

    async def execute(
        self, 
        query: str, 
        top_k: int = 5,
        enable_crag: Optional[bool] = None,
    ) -> List[SearchResult]:
        """Execute the hybrid search flow with optional CRAG fallback.
        
        Args:
            query: Search query
            top_k: Number of results to return
            enable_crag: Override for CRAG setting (defaults to settings.crag_enabled)
            
        Returns:
            List of ranked SearchResult objects
        """
        # Resolve CRAG enablement
        crag_enabled = enable_crag if enable_crag is not None else settings.crag_enabled
        
        # 1. Hybrid Search (Vector + BM25)
        fetch_k = top_k * 3
        
        vector_results = await self.kb_repo.search_similar(query, top_k=fetch_k)
        keyword_results = await self.kb_repo.search_keyword(query, top_k=fetch_k)
        
        # 2. Merge and Deduplicate
        seen_ids = set()
        merged = []
        
        for res in vector_results + keyword_results:
            if res.id not in seen_ids:
                seen_ids.add(res.id)
                merged.append(res)
        
        # 3. Rerank
        if merged:
            reranked = await self.reranker.rerank(query, merged, top_k=top_k)
        else:
            reranked = []
        
        # 4. CRAG: Evaluate quality and fallback to web search if needed
        if crag_enabled and self.web_search:
            quality_score = self._evaluate_quality(reranked)
            
            if quality_score < CRAG_QUALITY_THRESHOLD:
                logger.info(f"CRAG triggered: KB quality score {quality_score:.2f} < threshold {CRAG_QUALITY_THRESHOLD}")
                web_results = await self.web_search.search(query, num_results=top_k)
                
                # Merge web results with KB results
                for web_res in web_results:
                    if web_res.id not in seen_ids:
                        seen_ids.add(web_res.id)
                        reranked.append(web_res)
                
                # Limit to top_k after merging
                reranked = reranked[:top_k]
        
        return reranked
    
    def _evaluate_quality(self, results: List[SearchResult]) -> float:
        """Evaluate the quality of search results.
        
        Returns the top-1 rerank score, or -999 if no results.
        """
        if not results:
            return -999.0
        return results[0].score if results[0].score is not None else -999.0

    def format_for_llm(self, query: str, results: List[SearchResult]) -> str:
        """Format search results for LLM consumption.
        
        Args:
            query: Original query
            results: Search results
            
        Returns:
            Formatted string ready for LLM context
        """
        if not results:
            return f"### Search found 0 documents for: {query}"
        
        output_lines = [f"### Search found {len(results)} documents:"]
        
        for i, doc in enumerate(results, 1):
            # Extract source from metadata
            metadata = doc.metadata or {}
            source = metadata.get("source") or metadata.get("file_name") or metadata.get("title") or "unknown"
            
            # Handle web search results
            url = metadata.get("url", "")
            title = metadata.get("title", "")
            
            if url:
                source = f"{title} ({url})" if title else url
            
            score = doc.score if doc.score is not None else 0.0
            
            doc_info = (
                f"[{i}] Document (Score: {score:.2f})\n"
                f"   Source: {source}\n"
                f"   Content: {doc.content}\n"
            )
            output_lines.append(doc_info)
        
        return "\n".join(output_lines)
