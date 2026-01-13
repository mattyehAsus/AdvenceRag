"""Web Search Tool - Network search capabilities."""

import logging
from typing import Any
import httpx

from advence_rag.config import get_settings

logger = logging.getLogger(__name__)


async def search_serper(query: str, num_results: int = 5) -> dict[str, Any]:
    """Execute a Serper.dev Google Search asynchronously.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        dict: Standardized search results
    """
    settings = get_settings()
    api_key = settings.serper_api_key

    if not api_key:
        logger.warning("Serper API Key not configured")
        return {
            "status": "error",
            "error": "Serper API Key not configured",
            "results": [],
        }

    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": min(num_results, 20), # Serper supports more than 10
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
            # Check for Rate Limit (429) specifically
            if response.status_code == 429:
                return {
                    "status": "error",
                    "error": "Serper Rate Limit",
                    "code": 429,
                    "results": [],
                }
                
            response.raise_for_status()
            data = response.json()

        # Process results
        search_results = []
        if "organic" in data:
            for item in data["organic"]:
                search_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "serper_search",
                })

        return {
            "status": "success",
            "query": query,
            "count": len(search_results),
            "results": search_results,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Serper Search API error: {e.response.text}")
        return {
            "status": "error",
            "error": f"API Error: {e.response.status_code}",
            "code": e.response.status_code,
            "results": [],
        }
    except Exception as e:
        logger.error(f"Serper Search failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "results": [],
        }


async def search_web(query: str, num_results: int = 5) -> dict[str, Any]:
    """Unified web search interface with smart fallback.
    
    Tries the configured primary provider first. If it fails (especially due to rate limits),
    it automatically falls back to the other provider if configured.
    """
    settings = get_settings()
    primary = settings.search_provider
    
    # Define provider functions
    providers = {
        "google": search_google,
        "serper": search_serper
    }
    
    ordered_providers = []
    if primary in providers:
        ordered_providers.append(primary)
        # Add the other one as fallback
        other = "google" if primary == "serper" else "serper"
        ordered_providers.append(other)
    else:
        # Default fallback order if primary is invalid
        ordered_providers = ["serper", "google"]

    last_error = "No providers configured"
    
    for provider_name in ordered_providers:
        search_func = providers[provider_name]
        logger.info(f"Attempting web search with provider: {provider_name}")
        
        result = await search_func(query, num_results)
        
        if result["status"] == "success":
            return result
        
        # Log error and decide whether to fallback
        error_msg = result.get("error", "Unknown error")
        error_code = result.get("code")
        
        # If it's a configuration error (key missing), we should definitely try fallback
        # If it's a rate limit error (429), try fallback
        logger.warning(f"Search provider {provider_name} failed: {error_msg}")
        last_error = error_msg
        
        # Special case: Google search implementation above doesn't return "code" yet
        # but check for 429 or "not configured"
        if "not configured" in error_msg or error_code == 429 or "Rate Limit" in error_msg:
            continue
        
        # For other errors, we might still want to try the fallback anyway for robustness
        continue
        
    return {
        "status": "error",
        "error": f"All search providers failed. Last error: {last_error}",
        "results": [],
    }


async def search_google(query: str, num_results: int = 5) -> dict[str, Any]:
    """Execute a Google Custom Search asynchronously.

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
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            # Check for Rate Limit (429) specifically for fallback logic
            if response.status_code == 429:
                return {
                    "status": "error",
                    "error": "Google Rate Limit",
                    "code": 429,
                    "results": [],
                }
                
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
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Search API error: {e.response.text}")
        return {
            "status": "error",
            "error": f"API Error: {e.response.status_code}",
            "code": e.response.status_code,
            "results": [],
        }
    except Exception as e:
        logger.error(f"Google Search failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "results": [], 
        }
