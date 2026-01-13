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

import asyncio

async def verify_crag():
    print("--- Verifying CRAG Logic ---")
    
    # 1. Setup Data
    doc_id = "crag_test_doc"
    doc_content = "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability."
    
    print("\n1. Ingesting test document...")
    add_res = await add_documents([doc_content], ids=[doc_id], metadatas=[{"source": "test"}])
    print(f"   Add result: {add_res}")
    # Small sleep to ensure persistence
    await asyncio.sleep(0.5)
    
    try:
        # 2. Test Relevant Query
        print("\n2. Testing Relevant Query: 'Python programming'")
        from advence_rag.tools.knowledge_base import search_similar
        from advence_rag.tools.rerank import rerank_results
        
        # 1. Vector Search
        res_similar = await search_similar("Python programming", top_k=1)
        
        # 2. Rerank (to get rerank_score)
        res_reranked = await rerank_results("Python programming", res_similar["results"], top_k=1)
        
        # 3. Evaluate
        eval_rel = evaluate_retrieval_quality("Python programming", res_reranked["results"])
        
        print(f"   Score: {eval_rel['score']:.4f}")
        print(f"   Needs Web Search: {eval_rel['needs_web_search']}")
        print(f"   Reason: {eval_rel.get('reason')}")
        
        if eval_rel['needs_web_search']:
            print("❌ Error: Relevant document marked as needing web search!")
        else:
            print("✅ Correctly identified as Relevant.")
            
        # 3. Test Irrelevant Query
        print("\n3. Testing Irrelevant Query: 'How to bake a pizza'")
        res_irrelevant_v = await search_similar("How to bake a pizza", top_k=1)
        res_irrelevant_r = await rerank_results("How to bake a pizza", res_irrelevant_v["results"], top_k=1)
        
        if not res_irrelevant_r["results"]:
             print("   (No results found by vector search)")
             score = 0.0
        else:
             # Evaluate
             eval_irrel = evaluate_retrieval_quality("How to bake a pizza", res_irrelevant_r["results"])
             print(f"   Score: {eval_irrel['score']:.4f}")
             print(f"   Needs Web Search: {eval_irrel['needs_web_search']}")
             
             if not eval_irrel['needs_web_search']:
                 print("❌ Error: Irrelevant document NOT marked for web search!")
             else:
                 print("✅ Correctly identified as Irrelevant (Triggering Web Search).")

    finally:
        # Cleanup
        await delete_documents([doc_id])
        print("\nCleanup done.")

if __name__ == "__main__":
    asyncio.run(verify_crag())
