"""Web Search Tool - Network search capabilities."""

import logging
from typing import Any

import requests

from advence_rag.config import get_settings

logger = logging.getLogger(__name__)


def search_google(query: str, num_results: int = 5) -> dict[str, Any]:
    """Execute a Google Custom Search.

    Args:
        query: Search query
        num_results: Number of results to return (max 10)

    Returns:
        dict: Standardized search results
    """
    settings = get_settings()
    
    # 1. Check configuration
    api_key = settings.google_search_api_key or settings.google_api_key
    cse_id = settings.google_search_cse_id
    
    if not api_key:
        logger.warning("Google Search API Key not configured")
        return {
            "status": "error",
            "error": "Google Search API Key not configured",
            "results": [],
        }
        
    if not cse_id:
        logger.warning("Google CSE ID not configured")
        return {
            "status": "error",
            "error": "Google CSE ID not configured",
            "results": [],
        }

    # 2. Call Google API
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(num_results, 10),
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 3. Process results
        search_results = []
        if "items" in data:
            for item in data["items"]:
                search_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "google_search",
                })
                
        return {
            "status": "success",
            "query": query,
            "count": len(search_results),
            "results": search_results,
        }
        
    except Exception as e:
        logger.error(f"Google Search failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "results": [],
        }
