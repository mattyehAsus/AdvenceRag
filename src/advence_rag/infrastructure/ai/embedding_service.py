import logging
from typing import List
import asyncio

from google import genai
from advence_rag.domain.interfaces import EmbeddingService
from advence_rag.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GeminiEmbeddingService(EmbeddingService):
    """Implementation of EmbeddingService using Google Gemini API."""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_id = settings.embedding_model

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            # Run in thread because genai client might be blocking or we want to avoid event loop lag
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=self.model_id,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
            
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=self.model_id,
                contents=texts
            )
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            logger.error(f"Gemini batch embedding failed: {e}")
            raise

class LocalEmbeddingService(EmbeddingService):
    """Implementation of EmbeddingService using local sentence-transformers models."""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        if self.model_name.startswith("models/"):
            # Fallback for when someone switches to local but keeps the default Gemini path
            self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.warning(f"Incompatible Gemini model path for local embedding. Falling back to: {self.model_name}")
            
        self.device = settings.local_embedding_device
        self._model = None

    @property
    def model(self):
        """Lazy load the sentence-transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local embedding model: {self.model_name} on {self.device}")
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text locally."""
        # Non-blocking run of model.encode if it's CPU bound
        embeddings = await asyncio.to_thread(self.model.encode, [text])
        return embeddings[0].tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts locally."""
        if not texts:
            return []
        embeddings = await asyncio.to_thread(self.model.encode, texts)
        return embeddings.tolist()
