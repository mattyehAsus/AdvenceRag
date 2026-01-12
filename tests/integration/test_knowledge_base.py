import pytest
from advence_rag.tools.knowledge_base import (
    add_documents, 
    search_similar, 
    search_keyword, 
    delete_documents,
    _get_bm25_index
)

def test_add_and_search_vector(sample_docs, sample_ids, sample_metadatas):
    """Test adding documents and retrieving them via vector search."""
    # Add documents
    result = add_documents(sample_docs, ids=sample_ids, metadatas=sample_metadatas)
    assert result["status"] == "success"
    assert result["added_count"] == 4

    # Search (Vector)
    # Search for something related to the first doc
    search_res = search_similar("multi-agent system", top_k=1)
    assert search_res["status"] == "success"
    assert len(search_res["results"]) > 0
    assert "multi-agent" in search_res["results"][0]["content"]

def test_search_keyword_bm25(sample_docs, sample_ids):
    """Test retrieving documents via keyword search (BM25)."""
    # Ensure docs are added (fixture might be shared or need re-add if not careful)
    # In this setup, they should already be in from the previous test if session dir is used,
    # but let's be safe and assume isolation per test if possible.
    # Actually, conftest.py's test_data_dir is session scoped, but Chroma/BM25 state persists.
    
    # Search for specific keyword "ADK"
    search_res = search_keyword("ADK", top_k=1)
    assert search_res["status"] == "success"
    assert len(search_res["results"]) > 0
    assert "ADK" in search_res["results"][0]["content"]
    assert search_res["results"][0]["id"] == "test_id_1"

def test_delete_documents(sample_ids):
    """Test deleting documents from both indexes."""
    # Delete the first doc
    del_res = delete_documents([sample_ids[0]])
    assert del_res["status"] == "success"
    assert del_res["deleted_count"] == 1
    
    # Verify it's gone from BM25
    index = _get_bm25_index()
    assert sample_ids[0] not in index.doc_ids
    
    # Verify it's not found in keyword search anymore
    search_res = search_keyword("multi-agent", top_k=10)
    found_ids = [r["id"] for r in search_res["results"]]
    assert sample_ids[0] not in found_ids
