import sys
import shutil
from pathlib import Path

# Add src to sys.path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

def verify_search():
    print("--- Verifying Search Agent with Chroma ---")
    
    # 1. Setup Test Data
    from advence_rag.tools.knowledge_base import add_documents, delete_documents, search_similar
    from advence_rag.config import get_settings
    
    settings = get_settings()
    # Use a test collection if possible, or just be careful
    print(f"Using collection: {settings.chroma_collection_name}")
    
    test_docs = [
        "Google Agent Development Kit (ADK) 是一個強大的框架。",
        "RAG (Retrieval Augmented Generation) 結合了檢索與生成。",
        "Chroma 是一個開源的向量資料庫。",
    ]
    test_ids = ["test_doc_1", "test_doc_2", "test_doc_3"]
    
    try:
        # Clean up previous test data
        print("Cleaning up previous test data...")
        delete_documents(test_ids)
        
        # 2. Ingest Data
        print(f"\nIngesting {len(test_docs)} test documents...")
        add_result = add_documents(
            documents=test_docs,
            metadatas=[{"source": "test"}] * 3,
            ids=test_ids
        )
        print(f"Ingestion result: {add_result}")
        
        # 3. Test Search Tool directly
        print("\nTesting search_similar tool...")
        query = "什麼是 ADK?"
        tool_result = search_similar(query, top_k=2)
        print(f"Query: {query}")
        print(f"Found: {len(tool_result['results'])} documents")
        for doc in tool_result['results']:
            print(f"  - {doc['content'][:50]}... (dist: {doc['distance']:.4f})")
            
        # 4. Test Search Agent Function
        print("\nTesting search_agent function wrapper...")
        from advence_rag.agents.search import search_knowledge_base
        agent_result = search_knowledge_base(query, top_k=1)
        print(f"Agent Wrapper Result keys: {agent_result.keys()}")
        print(f"Top result: {agent_result['results'][0]['content'] if agent_result['results'] else 'None'}")

        # Cleanup
        print("\nCleaning up...")
        delete_documents(test_ids)
        
        print("\n✅ Search Verification Complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Search Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_search()
