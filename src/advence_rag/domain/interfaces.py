from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from advence_rag.domain.entities import Document, SearchResult

class KnowledgeBaseRepository(ABC):
    """Interface for document storage and retrieval."""
    
    @abstractmethod
    async def add_documents(
        self, 
        documents: List[Document], 
        ids: Optional[List[str]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def search_similar(self, query: str, top_k: int = 5) -> List[SearchResult]:
        pass

    @abstractmethod
    async def search_keyword(self, query: str, top_k: int = 5) -> List[SearchResult]:
        pass

    @abstractmethod
    async def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        pass

class RerankerService(ABC):
    """Interface for reranking search results."""
    
    @abstractmethod
    async def rerank(self, query: str, documents: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        pass

class LLMAgentService(ABC):
    """Interface for orchestrating agentic RAG workflows."""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        pass


class WebSearchService(ABC):
    """Interface for web search capabilities (CRAG fallback)."""
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        pass

class EmbeddingService(ABC):
    """Interface for generating text embeddings."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass
