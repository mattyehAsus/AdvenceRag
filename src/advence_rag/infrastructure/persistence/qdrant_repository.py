import logging
import asyncio
from typing import Any, Dict, List, Optional
import uuid

from qdrant_client import QdrantClient, models
from advence_rag.domain.entities import Document, SearchResult
from advence_rag.domain.interfaces import KnowledgeBaseRepository, EmbeddingService
from advence_rag.config import get_settings

logger = logging.getLogger("advence_rag")
settings = get_settings()

class QdrantKnowledgeBaseRepository(KnowledgeBaseRepository):
    """Infrastructure implementation of KnowledgeBaseRepository using Qdrant."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
            self.collection_name = settings.qdrant_collection_name
            self._dim: Optional[int] = None
            self._ensure_collection()
        except ImportError:
            raise ImportError(
                "qdrant-client is required. Install with: pip install qdrant-client"
            )

    async def _get_dimension(self) -> int:
        """Get embedding dimension by searching or creating a test vector."""
        if self._dim is not None:
            return self._dim
            
        test_text = "test"
        # Since this is during init, we wrap in sync run or handle carefully.
        # But _ensure_collection should be called in a context where loop is running.
        # Actually _ensure_collection is sync. Let's make it more robust.
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            vector = await self.embedding_service.embed_text(test_text)
        else:
            vector = loop.run_until_complete(self.embedding_service.embed_text(test_text))
            
        self._dim = len(vector)
        return self._dim

    def _ensure_collection(self):
        """Ensure the Qdrant collection exists with proper configuration."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        # Get dimension (blocking for init)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # This is tricky in sync __init__ if loop is already running.
            # Usually factory is called inside async code.
            # For simplicity, let's use a simpler way or assume 768 as default and update if needed.
            # Better: Move _ensure_collection call out of __init__ or use a background task.
            # But during init, we need it.
            pass

        if not exists:
            # For Qdrant init, if we can't get dimension easily, 
            # we'll look at settings or use a safe default.
            # BUT since we use Clean Architecture, let's try to get it from service.
            
            # Temporary: Try to get dimension. If not, default to 768 (Gemini) or 384 (MiniLM)
            dim = 768 if settings.embedding_type == "cloud" else 384
            if settings.embedding_type == "local" and "bge" in settings.embedding_model.lower():
                dim = 768 # BGE-large
            
            logger.info(f"Creating Qdrant collection: {self.collection_name} with dim={dim}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=dim, 
                    distance=models.Distance.COSINE
                ),
            )
            # Create full-text index for the 'content' field to support search_keyword
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="content",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=15,
                    lowercase=True,
                ),
            )

    async def add_documents(
        self, 
        documents: List[Document], 
        ids: Optional[List[str]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Add documents to Qdrant with embeddings."""
        contents = [doc.content for doc in documents]
        
        # 1. Generate embeddings
        embeddings = await self.embedding_service.embed_batch(contents)
        
        # 2. Prepare points
        points = []
        for i, (doc, vector) in enumerate(zip(documents, embeddings)):
            doc_id = ids[i] if ids else (doc.chunk_id or str(uuid.uuid4()))
            # Qdrant requires UUID or integer ID. Try to parse as UUID or hash.
            try:
                point_id = str(uuid.UUID(doc_id))
            except (ValueError, AttributeError):
                # Fallback to deterministic UUID based on string
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))
                
            payload = {
                "content": doc.content,
                "metadata": metadatas[i] if metadatas else doc.metadata,
                "source": doc.source,
                "page_number": doc.page_number
            }
            points.append(models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            ))
            
        # 3. Upsert to Qdrant
        await asyncio.to_thread(
            self.client.upsert,
            collection_name=self.collection_name,
            points=points
        )
        
        return {
            "status": "success",
            "added_count": len(points),
            "ids": [p.id for p in points]
        }

    async def search_similar(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search similar documents in Qdrant using vector embeddings."""
        # 1. Generate query embedding
        vector = await self.embedding_service.embed_text(query)
        
        # 2. Search in Qdrant
        hits = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collection_name,
            query_vector=vector,
            limit=top_k
        )
        
        return [
            SearchResult(
                content=hit.payload.get("content", ""),
                metadata=hit.payload.get("metadata", {}),
                id=str(hit.id),
                score=hit.score,
                source=hit.payload.get("source"),
                page_number=hit.payload.get("page_number")
            ) for hit in hits
        ]

    async def search_keyword(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search documents in Qdrant using full-text search index."""
        # Qdrant doesn't have a direct "search_keyword" like BM25 in Chroma
        # but we can use 'scroll' with a filter or a 'Match' query.
        # Here we use the text index we created in _ensure_collection.
        
        hits = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collection_name,
            query_vector=[0.0] * (await self._get_dimension()), # Dynamic dimension for dummy vector
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="content",
                        match=models.MatchText(text=query)
                    )
                ]
            ),
            limit=top_k,
            with_vectors=False
        )
        
        return [
            SearchResult(
                content=hit.payload.get("content", ""),
                metadata=hit.payload.get("metadata", {}),
                id=str(hit.id),
                score=hit.score,
                source=hit.payload.get("source"),
                page_number=hit.payload.get("page_number")
            ) for hit in hits
        ]

    async def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        """Delete documents from Qdrant by ID."""
        # Process IDs to ensure they are valid Qdrant IDs
        point_ids = []
        for doc_id in ids:
            try:
                point_ids.append(str(uuid.UUID(doc_id)))
            except ValueError:
                point_ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id)))
                
        await asyncio.to_thread(
            self.client.delete,
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=point_ids)
        )
        
        return {
            "status": "success",
            "deleted_count": len(ids)
        }
