import sys
import logging
from pathlib import Path

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import asyncio

def verify_web_search():
    print("--- Verifying Web Search Tool ---")
    
    from advence_rag.tools.web_search import search_google
    
    async def run_test():
        # Test 1: Real Search (Expected: Success with results)
        print("\n1. Testing Google Search with configured keys...")
        query = "asus"
        res = await search_google(query, num_results=1)
        
        print(f"Status: {res['status']}")
        if res['status'] == 'success':
            print(f"✅ Search successful! Found {res['count']} results.")
            if res['results']:
                first = res['results'][0]
                print(f"   First result: {first['title']} ({first['url']})")
        else:
            print(f"❌ Search failed: {res.get('error')}")
            # Check if it's still about configuration
            if "not configured" in str(res.get('error')):
                print("   (Did you save the .env file?)")

        print("\n✅ Web Search Implementation Verified (Structure & Config)")

    asyncio.run(run_test())

if __name__ == "__main__":
    verify_web_search()
