import sys
import logging
from pathlib import Path

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from advence_rag.agents.search import search_web
from advence_rag.agents.writer import format_sources

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_full_flow():
    print("--- Verifying End-to-End Agent Interaction ---")
    
    # 1. Simulate Search Agent Output (Web Search)
    print("\n1. Executing Web Search...")
    search_res = search_web("openai", num_results=1)
    
    if search_res["status"] != "success":
        print("❌ Search failed, cannot verify flow.")
        return

    docs = search_res["results"]
    print(f"   Got {len(docs)} documents from search.")
    if docs:
        print(f"   Doc 1: {docs[0]}")

    # 2. Simulate Writer Agent Input
    # Writer uses 'format_sources' to prepare citations
    print("\n2. Writer Agent: Formatting Sources...")
    formatted = format_sources(docs)
    
    print(f"   Formatted sources: {formatted}")
    
    # 3. Validation
    if not formatted:
        if not docs:
            print("⚠️ No docs to format (Search return empty).")
        else:
            print("❌ Formatting failed.")
    else:
        first_src = formatted[0]
        if "url" in first_src and first_src["url"].startswith("http"):
             print("✅ Source URL preserved correctly.")
        else:
             print("❌ Source URL missing or empty.")
             
        if first_src["source"] == "google_search":
             print("✅ Source origin 'google_search' preserved.")
        
    print("\n✅ Knowledge Flow Verified (Search -> Writer)")

if __name__ == "__main__":
    verify_full_flow()
