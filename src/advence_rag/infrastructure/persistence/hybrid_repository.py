import logging
from typing import Any, Dict, List, Optional

from advence_rag.domain.entities import Document, SearchResult
from advence_rag.domain.interfaces import KnowledgeBaseRepository
from advence_rag.infrastructure.persistence.repository_factory import get_repository

logger = logging.getLogger("advence_rag")

class HybridKnowledgeBaseRepository(KnowledgeBaseRepository):
    """
    Backward-compatible wrapper that delegates to the configured repository implementation.
    This class now acts as a proxy to the repository factory.
    """
    
    def __init__(self):
        self._repo = get_repository()

    async def add_documents(
        self, 
        documents: List[Document], 
        ids: Optional[List[str]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        return await self._repo.add_documents(documents, ids=ids, metadatas=metadatas)

    async def search_similar(self, query: str, top_k: int = 5) -> List[SearchResult]:
        return await self._repo.search_similar(query, top_k=top_k)

    async def search_keyword(self, query: str, top_k: int = 5) -> List[SearchResult]:
        return await self._repo.search_keyword(query, top_k=top_k)

    async def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        return await self._repo.delete_documents(ids)
