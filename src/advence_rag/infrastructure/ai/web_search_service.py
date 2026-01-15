"""Web Search Service - Infrastructure implementation of WebSearchService."""

from typing import List
import logging

from advence_rag.domain.entities import SearchResult
from advence_rag.domain.interfaces import WebSearchService
from advence_rag.tools.web_search import search_web

logger = logging.getLogger(__name__)


class SerperWebSearchService(WebSearchService):
    """Infrastructure implementation of WebSearchService using Serper/Google."""
    
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Execute web search and return domain-typed results."""
        result = await search_web(query, num_results)
        
        if result["status"] != "success":
            logger.warning(f"Web search failed: {result.get('error')}")
            return []
        
        return [
            SearchResult(
                content=r.get("snippet", ""),
                metadata={
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", "web_search"),
                },
                id=r.get("url", ""),  # Use URL as ID for web results
                score=0.0,  # Web results don't have scores
            )
            for r in result.get("results", [])
        ]
