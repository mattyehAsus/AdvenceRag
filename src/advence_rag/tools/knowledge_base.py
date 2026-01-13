import logging
import pickle
import asyncio
from pathlib import Path
from typing import Any

from advence_rag.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global state for lazy initialization
_chroma_client = None
_collection = None
_bm25_index = None


class BM25Index:
    """Simple wrapper for rank_bm25 with persistence."""
    
    def __init__(self, persist_path: Path):
        self.persist_path = persist_path
        self.corpus: list[str] = []
        self.doc_ids: list[str] = []
        self.bm25 = None
        self._load()

    def _load(self):
        if self.persist_path.exists():
            try:
                with open(self.persist_path, "rb") as f:
                    data = pickle.load(f)
                    self.corpus = data.get("corpus", [])
                    self.doc_ids = data.get("doc_ids", [])
                    self._rebuild_model()
            except Exception as e:
                logger.error(f"Failed to load BM25 index: {e}")

    def _save(self):
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, "wb") as f:
                pickle.dump({
                    "corpus": self.corpus,
                    "doc_ids": self.doc_ids
                }, f)
        except Exception as e:
            logger.error(f"Failed to save BM25 index: {e}")

    def _rebuild_model(self):
        if not self.corpus:
            self.bm25 = None
            return
        
        from rank_bm25 import BM25Okapi
        # Simple tokenization: lower case and split. 
        # Future: Use tiktoken or specialized tokenizer.
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def add(self, documents: list[str], ids: list[str]):
        self.corpus.extend(documents)
        self.doc_ids.extend(ids)
        self._rebuild_model()
        self._save()

    def delete(self, ids: list[str]):
        ids_set = set(ids)
        new_corpus = []
        new_ids = []
        for doc, d_id in zip(self.corpus, self.doc_ids):
            if d_id not in ids_set:
                new_corpus.append(doc)
                new_ids.append(d_id)
        
        self.corpus = new_corpus
        self.doc_ids = new_ids
        self._rebuild_model()
        self._save()

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        if not self.bm25:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        import numpy as np
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0: # Only return if there's some match
                results.append({
                    "content": self.corpus[idx],
                    "id": self.doc_ids[idx],
                    "bm25_score": float(scores[idx]),
                    "source": "bm25"
                })
        return results


def _get_bm25_index() -> BM25Index:
    global _bm25_index
    if _bm25_index is None:
        persist_path = Path(settings.chroma_persist_directory) / "bm25_index.pkl"
        _bm25_index = BM25Index(persist_path)
    return _bm25_index


def _get_collection():
    """Get or create Chroma collection (lazy initialization)."""
    global _chroma_client, _collection
    
    if _collection is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            _chroma_client = chromadb.PersistentClient(
                path=str(settings.chroma_persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            _collection = _chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except ImportError:
            raise ImportError(
                "chromadb is required. Install with: pip install chromadb"
            )
    
    return _collection


async def search_similar(
    query: str,
    top_k: int | None = None,
    filter_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """從知識庫檢索相似文檔。
    
    Args:
        query: 查詢文字
        top_k: 返回結果數量，預設使用設定值
        filter_metadata: 可選的 metadata 過濾條件
        
    Returns:
        dict: 包含檢索結果的字典
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    
    try:
        collection = _get_collection()
        
        # Wrap blocking ChromaDB call in thread
        results = await asyncio.to_thread(
            collection.query,
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )
        
        documents = []
        for i, doc in enumerate(results["documents"][0]):
            documents.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0,
                "id": results["ids"][0][i] if results["ids"] else f"doc_{i}",
            })
        
        return {
            "status": "success",
            "query": query,
            "results": documents,
            "total_found": len(documents),
        }
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "results": [],
            "total_found": 0,
        }


async def search_keyword(
    query: str,
    top_k: int | None = None,
) -> dict[str, Any]:
    """使用 BM25 進行關鍵字檢索。
    
    Args:
        query: 查詢文字
        top_k: 返回結果數量
        
    Returns:
        dict: 包含檢索結果的字典
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
        
    try:
        index = _get_bm25_index()
        # BM25 search is CPU bound, run in thread
        results = await asyncio.to_thread(index.search, query, top_k=top_k)
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_found": len(results),
        }
    except Exception as e:
        logger.error(f"BM25 search failed: {e}")
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "results": [],
            "total_found": 0,
        }


async def add_documents(
    documents: list[str],
    metadatas: list[dict[str, Any]] | None = None,
    ids: list[str] | None = None,
) -> dict[str, Any]:
    """新增文檔到知識庫。
    
    Args:
        documents: 文檔內容列表
        metadatas: 對應的 metadata 列表
        ids: 文檔 ID 列表，若不提供則自動生成
        
    Returns:
        dict: 操作結果
    """
    try:
        collection = _get_collection()
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        # Blocking ChromaDB write
        await asyncio.to_thread(
            collection.add,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        
        # 2. Update BM25 Index
        try:
            index = _get_bm25_index()
            # BM25 update involves rebuilding model and disk write
            await asyncio.to_thread(index.add, documents, ids)
        except Exception as e:
            logger.error(f"Failed to update BM25 index: {e}")
        
        return {
            "status": "success",
            "added_count": len(documents),
            "ids": ids,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "added_count": 0,
        }


async def delete_documents(ids: list[str]) -> dict[str, Any]:
    """從知識庫刪除文檔。
    
    Args:
        ids: 要刪除的文檔 ID 列表
        
    Returns:
        dict: 操作結果
    """
    try:
        collection = _get_collection()
        await asyncio.to_thread(collection.delete, ids=ids)
        
        # Update BM25 Index
        try:
            index = _get_bm25_index()
            await asyncio.to_thread(index.delete, ids)
        except Exception as e:
            logger.error(f"Failed to delete from BM25 index: {e}")
            
        return {
            "status": "success",
            "deleted_count": len(ids),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "deleted_count": 0,
        }
