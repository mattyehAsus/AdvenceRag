import sys
import logging
from pathlib import Path
import asyncio

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_tools():
    print("--- Verifying Agent Tools Directly ---")
    
    # 1. Guard Tools
    print("\n1. Testing Guard Tools...")
    from advence_rag.agents.guard import check_sensitive_content, validate_query
    
    res = check_sensitive_content("My phone number is 0912-345-678") # Not matching regex exactly?
    # Default patterns: \d{3}-?\d{2}-?\d{4} (US SSN)
    # [A-Z][12]\d{8} (TW ID)
    
    tw_id_safe = "A123456789"
    res_tw = check_sensitive_content(f"My ID is {tw_id_safe}")
    print(f"TW ID Check: {res_tw['is_safe']} (Expected: False)")
    
    safe_query = "What is RAG?"
    res_query = validate_query(safe_query)
    print(f"Query Check '{safe_query}': {res_query['status']}")
    
    if not res_query['can_proceed']:
        print("Guard Validation Failed on Safe Query!")

    # 2. Search Tools
    print("\n2. Testing Search Tools...")
    from advence_rag.agents.search import search_knowledge_base, search_web, evaluate_retrieval_quality
    
    # We might need to ensure DB is clean or has data. verify_ingestion handled that.
    # Just checking execution.
    try:
        search_res = search_knowledge_base("RAG", top_k=1)
        print(f"Search Tool Result: Found {len(search_res.get('results', []))} docs")
    except Exception as e:
        print(f"Search Tool Error: {e}")

    eval_res = evaluate_retrieval_quality("RAG", [])
    print(f"Eval Quality (Empty): {eval_res['quality']} (Expected: poor)")
    
    web_res = search_web("RAG")
    print(f"Web Search (Mock): {web_res['status']}")

    # 3. Planner Tools
    print("\n3. Testing Planner Tools...")
    from advence_rag.agents.planner import create_search_plan
    plan = create_search_plan(["What is RAG?", "How does it work?"])
    print(f"Planner Plan: {plan['queries']}")

    # 4. Writer Tools
    print("\n4. Testing Writer Tools...")
    from advence_rag.agents.writer import format_sources, add_disclaimer_if_needed
    
    docs = [{"title": "Doc A", "source": "KB", "url": "http://a.com"}]
    sources = format_sources(docs)
    print(f"Formatted Sources: {sources}")
    
    disc = add_disclaimer_if_needed("Answer.", confidence=0.5, has_web_sources=True)
    print(f"Disclaimer Added: {len(disc) > len('Answer.')}")

    print("\n✅ All Tool Verifications Complete")

if __name__ == "__main__":
    verify_tools()
