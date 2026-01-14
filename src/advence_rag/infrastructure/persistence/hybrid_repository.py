import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from advence_rag.domain.entities import Document, SearchResult
from advence_rag.domain.interfaces import KnowledgeBaseRepository
from advence_rag.config import get_settings

logger = logging.getLogger("advence_rag")
settings = get_settings()

class HybridKnowledgeBaseRepository(KnowledgeBaseRepository):
    """Infrastructure implementation of KnowledgeBaseRepository using ChromaDB and BM25."""
    
    def __init__(self):
        # We'll import these here to avoid circular dependencies if any
        # and to keep the interface clean.
        from advence_rag.tools.knowledge_base import (
            add_documents as _add,
            search_similar as _search_v,
            search_keyword as _search_k,
            delete_documents as _delete
        )
        self._add = _add
        self._search_v = _search_v
        self._search_k = _search_k
        self._delete = _delete

    async def add_documents(
        self, 
        documents: List[Document], 
        ids: Optional[List[str]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # Convert domain objects to raw lists for existing tool
        doc_contents = [doc.content for doc in documents]
        
        # Extract IDs and metadatas from Document objects if not provided
        if ids is None:
            ids = [doc.chunk_id for doc in documents]
        if metadatas is None:
            metadatas = [doc.metadata for doc in documents]
            
        return await self._add(doc_contents, ids=ids, metadatas=metadatas)

    async def search_similar(self, query: str, top_k: int = 5) -> List[SearchResult]:
        res = await self._search_v(query, top_k=top_k)
        if res["status"] != "success":
            return []
        return [
            SearchResult(
                content=r["content"],
                metadata=r["metadata"],
                id=r["id"],
                score=r["distance"]
            ) for r in res["results"]
        ]

    async def search_keyword(self, query: str, top_k: int = 5) -> List[SearchResult]:
        res = await self._search_k(query, top_k=top_k)
        if res["status"] != "success":
            return []
        return [
            SearchResult(
                content=r["content"],
                metadata=r["metadata"],
                id=r["id"],
                score=r["score"]
            ) for r in res["results"]
        ]

    async def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        return await self._delete(ids)
