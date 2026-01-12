import pytest
from unittest.mock import patch, MagicMock
from advence_rag.agents.search import search_knowledge_base

def test_search_pipeline_deduplication(populated_knowledge_base):
    """Test that the pipeline correctly deduplicates results from vector and keyword search."""
    # "coordination" is in doc 2: "It uses Google ADK for coordination."
    # Vector search might find it, and Keyword search definitely will.
    
    query = "coordination"
    results = search_knowledge_base(query, top_k=5)
    
    assert results["status"] == "success"
    
    # Extract IDs
    ids = [res["id"] for res in results["results"]]
    
    # Check for duplicates
    assert len(ids) == len(set(ids)), f"Duplicate IDs found in results: {ids}"
    assert "test_id_1" in ids

def test_search_pipeline_keyword_strength(populated_knowledge_base):
    """Test that exact keyword matches (BM25) are prioritized or included."""
    # "ADK" is an exact keyword in doc 2
    query = "ADK"
    results = search_knowledge_base(query, top_k=5)
    
    assert results["status"] == "success"
    ids = [res["id"] for res in results["results"]]
    assert "test_id_1" in ids

def test_search_pipeline_reranking_flow(populated_knowledge_base):
    """Test the reranking flow in the retrieval pipeline."""
    # We want to verify that the reranker is called
    # In a real environment, it uses the local model downloaded during verify_hybrid.py.
    # Here we can either let it run (if we want full integration) or mock it.
    # Since we want to verify the logic of how it applies to the pipeline, 
    # let's mock it to see if it correctly receives and sorts.
    
    with patch("advence_rag.tools.rerank.rerank_results") as mock_rerank:
        # Mock rerank to reverse the order or something obvious
        def side_effect(query, documents, top_k):
            # Sort by ID descending just for testing
            sorted_results = sorted(documents, key=lambda x: x["id"], reverse=True)
            return {"status": "success", "results": sorted_results[:top_k]}
        
        mock_rerank.side_effect = side_effect
        
        query = "multi-agent"
        results = search_knowledge_base(query, top_k=2)
        
        assert results["status"] == "success"
        assert len(results["results"]) == 2
        # Check if they are sorted by ID descending as per our mock
        assert results["results"][0]["id"] > results["results"][1]["id"]
        mock_rerank.assert_called_once()

def test_search_pipeline_empty_query(populated_knowledge_base):
    """Test the pipeline with a query that returns no results."""
    # Since Vector DB usually returns nearest neighbors even for garbage,
    # we use a query that BM25 will definitely miss (0 overlap).
    # Currently SearchAgent doesn't filter vector results by threshold,
    # but Keyword search will be empty.
    query = "XYZ123NONEXISTENT"
    results = search_knowledge_base(query, top_k=5)
    
    assert results["status"] == "success"
    # Even if results are found via vector search, their distance should be high
    # if we had a filter. For now, we just ensure it doesn't crash.
    assert "results" in results
