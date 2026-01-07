"""Knowledge Base Tool - Chroma 向量資料庫操作。

提供知識庫的新增、檢索、刪除等操作。
"""

from typing import Any

from advence_rag.config import get_settings

settings = get_settings()

# Chroma client will be lazily initialized
_chroma_client = None
_collection = None


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


def search_similar(
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
        
        results = collection.query(
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


def add_documents(
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
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        
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


def delete_documents(ids: list[str]) -> dict[str, Any]:
    """從知識庫刪除文檔。
    
    Args:
        ids: 要刪除的文檔 ID 列表
        
    Returns:
        dict: 操作結果
    """
    try:
        collection = _get_collection()
        collection.delete(ids=ids)
        
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
