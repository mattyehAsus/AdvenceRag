"""Verification Script - Hybrid Search functionality."""

import sys
from pathlib import Path

# Add src to sys.path
_src_path = Path(__file__).resolve().parent.parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from advence_rag.tools.knowledge_base import add_documents, search_keyword, search_similar
from advence_rag.agents.search import search_knowledge_base

def test_hybrid():
    print("🛠️  Phase 1: Adding test data...")
    docs = [
        "Advence RAG uses Google ADK for multi-agent coordination.",
        "Chroma is the default vector database for this project.",
        "The system supports BM25 hybrid search for better accuracy.",
        "Version 0.1.0 was released in January 2026."
    ]
    ids = ["doc1", "doc2", "doc3", "doc4"]
    metadatas = [{"source": "test"} for _ in docs]
    
    add_res = add_documents(docs, ids=ids, metadatas=metadatas)
    print(f"Result: {add_res['status']}")
    if add_res['status'] == 'error':
        print(f"❌ Error message: {add_res.get('error')}")
    
    print("\n🔍 Phase 2: Testing Keyword Search (BM25)...")
    # Search for something very specific like "0.1.0"
    k_res = search_keyword("0.1.0", top_k=2)
    print(f"Keyword '0.1.0' search results: {len(k_res['results'])}")
    for r in k_res['results']:
        print(f" - [{r.get('id')}] Score: {r.get('bm25_score'):.2f}: {r.get('content')}")

    print("\n🚀 Phase 3: Testing Hybrid Search via Agent Logic...")
    h_res = search_knowledge_base("Tell me about Google ADK", top_k=2)
    print(f"Hybrid search results: {len(h_res['results'])}")
    print(f"Search type: {h_res.get('search_type')}")
    for r in h_res['results']:
        # Reranked results might have 'rerank_score'
        score = r.get('rerank_score', r.get('distance', 'N/A'))
        print(f" - [{r.get('id')}] Score: {score}: {r.get('content')[:50]}...")

if __name__ == "__main__":
    try:
        import chromadb
        import rank_bm25
        import numpy
        test_hybrid()
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install rank-bm25 numpy")
