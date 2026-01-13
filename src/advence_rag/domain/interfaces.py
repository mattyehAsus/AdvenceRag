from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from advence_rag.domain.entities import Document, SearchResult

class KnowledgeBaseRepository(ABC):
    """Interface for document storage and retrieval."""
    
    @abstractmethod
    def add_documents(
        self, 
        documents: List[Document], 
        ids: Optional[List[str]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def search_similar(self, query: str, top_k: int = 5) -> List[SearchResult]:
        pass

    @abstractmethod
    def search_keyword(self, query: str, top_k: int = 5) -> List[SearchResult]:
        pass

    @abstractmethod
    def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        pass

class RerankerService(ABC):
    """Interface for reranking search results."""
    
    @abstractmethod
    def rerank(self, query: str, documents: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        pass

class LLMAgentService(ABC):
    """Interface for orchestrating agentic RAG workflows."""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        pass
