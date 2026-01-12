"""Migration Utility - Rebuild BM25 index from Chroma data."""

import sys
from pathlib import Path

# Add src to sys.path
_src_path = Path(__file__).resolve().parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from advence_rag.tools.knowledge_base import _get_collection, _get_bm25_index

def rebuild():
    print("🚀 Starting BM25 index rebuild...")
    
    # 1. Get raw data from Chroma
    collection = _get_collection()
    results = collection.get(include=["documents"])
    
    documents = results.get("documents", [])
    ids = results.get("ids", [])
    
    if not documents:
        print("⚠️ No documents found in Chroma. Nothing to rebuild.")
        return

    print(f"📊 Found {len(documents)} documents in Chroma.")
    
    # 2. Re-initialize BM25 Index
    index = _get_bm25_index()
    # Clear existing
    index.corpus = []
    index.doc_ids = []
    
    # 3. Add all documents
    print("🔧 Tokenizing and indexing...")
    index.add(documents, ids)
    
    print(f"✅ Successfully rebuilt BM25 index at: {index.persist_path}")

if __name__ == "__main__":
    rebuild()
