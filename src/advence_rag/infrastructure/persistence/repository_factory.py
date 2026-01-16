import logging
from typing import Optional

from advence_rag.domain.interfaces import KnowledgeBaseRepository, EmbeddingService
from advence_rag.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_repository_instance: Optional[KnowledgeBaseRepository] = None
_embedding_service_instance: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Factory function to get the configured EmbeddingService instance."""
    global _embedding_service_instance
    
    if _embedding_service_instance is None:
        if settings.embedding_type == "cloud":
            from advence_rag.infrastructure.ai.embedding_service import GeminiEmbeddingService
            logger.info("Initializing Gemini Cloud Embedding Service")
            _embedding_service_instance = GeminiEmbeddingService()
        else:
            from advence_rag.infrastructure.ai.embedding_service import LocalEmbeddingService
            logger.info("Initializing Local (sentence-transformers) Embedding Service")
            _embedding_service_instance = LocalEmbeddingService()
        
    return _embedding_service_instance

def get_repository() -> KnowledgeBaseRepository:
    """Factory function to get the configured KnowledgeBaseRepository instance."""
    global _repository_instance
    
    if _repository_instance is None:
        db_type = settings.vector_db_type
        
        if db_type == "chroma":
            from advence_rag.infrastructure.persistence.chroma_repository import ChromaKnowledgeBaseRepository
            logger.info("Initializing ChromaDB Repository")
            _repository_instance = ChromaKnowledgeBaseRepository()
        elif db_type == "qdrant":
            from advence_rag.infrastructure.persistence.qdrant_repository import QdrantKnowledgeBaseRepository
            embedding_service = get_embedding_service()
            logger.info(f"Initializing Qdrant Repository at {settings.qdrant_url}")
            _repository_instance = QdrantKnowledgeBaseRepository(embedding_service)
        else:
            raise ValueError(f"Unsupported vector_db_type: {db_type}")
            
    return _repository_instance
