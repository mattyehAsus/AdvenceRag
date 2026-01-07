import sys
import logging
from pathlib import Path
import shutil

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from advence_rag.agents.search import search_knowledge_base, evaluate_retrieval_quality
from advence_rag.tools.knowledge_base import add_documents, delete_documents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_crag():
    print("--- Verifying CRAG Logic ---")
    
    # 1. Setup Data
    doc_id = "crag_test_doc"
    doc_content = "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability."
    
    print("\n1. Ingesting test document...")
    add_documents([doc_content], ids=[doc_id], metadatas=[{"source": "test"}])
    
    try:
        # 2. Test Relevant Query
        print("\n2. Testing Relevant Query: 'Python programming'")
        # search_knowledge_base now does reranking implicitly
        res_relevant = search_knowledge_base("Python programming", top_k=1)
        
        # Evaluate
        eval_rel = evaluate_retrieval_quality("Python programming", res_relevant["results"])
        print(f"   Score: {eval_rel['score']:.4f}")
        print(f"   Needs Web Search: {eval_rel['needs_web_search']}")
        
        if eval_rel['needs_web_search']:
            print("❌ Error: Relevant document marked as needing web search!")
        else:
            print("✅ Correctly identified as Relevant.")
            
        # 3. Test Irrelevant Query
        print("\n3. Testing Irrelevant Query: 'How to bake a pizza'")
        res_irrelevant = search_knowledge_base("How to bake a pizza", top_k=1)
        
        # Depending on vector search, it might return the python doc with low score, 
        # or nothing if distance is too far (but Chroma defaults usually return *something*)
        
        if not res_irrelevant["results"]:
             print("   (No results found by vector search)")
             score = 0.0
        else:
             # Evaluate
             eval_irrel = evaluate_retrieval_quality("How to bake a pizza", res_irrelevant["results"])
             print(f"   Score: {eval_irrel['score']:.4f}")
             print(f"   Needs Web Search: {eval_irrel['needs_web_search']}")
             
             if not eval_irrel['needs_web_search']:
                 print("❌ Error: Irrelevant document NOT marked for web search!")
             else:
                 print("✅ Correctly identified as Irrelevant (Triggering Web Search).")

    finally:
        # Cleanup
        delete_documents([doc_id])
        print("\nCleanup done.")

if __name__ == "__main__":
    verify_crag()
