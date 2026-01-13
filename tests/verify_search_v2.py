import sys
import logging
import asyncio
from pathlib import Path

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from advence_rag.tools.web_search import search_serper, search_web, search_google
from advence_rag.config import get_settings

async def verify_search():
    settings = get_settings()
    
    print("--- Verifying Search Provider Integration ---")
    
    # 1. Test Serper directamente
    print("\n1. Testing Serper.dev Search...")
    if not settings.serper_api_key:
        print("⚠️ Serper API Key not set in .env. Skipping direct test.")
    else:
        res = await search_serper("DeepSeek-V3", num_results=2)
        print(f"Status: {res['status']}")
        if res['status'] == 'success':
            print(f"✅ Serper search successful! Found {res['count']} results.")
            for r in res['results']:
                print(f"   - {r['title']} ({r['source']})")
        else:
            print(f"❌ Serper search failed: {res.get('error')}")

    # 2. Test Unified Search (Expected: Serper as default)
    print("\n2. Testing Unified search_web (Primary: Serper)...")
    res = await search_web("Best RAG practices", num_results=2)
    print(f"Status: {res['status']}")
    if res['status'] == 'success':
        print(f"✅ Unified search successful! Provider used: {res['results'][0]['source']}")
    else:
        print(f"❌ Unified search failed: {res.get('error')}")

    # 3. Test Fallback
    print("\n3. Testing Fallback Mechanism (Mocking Failure)...")
    # We can't easily mock here without monkeypatching, 
    # but we can observe logs if one is missing.
    if not settings.google_search_api_key:
        print("ℹ️ Google API Key missing. Checking if it falls back properly when Serper is 'gone'...")
        # Temporarily clear key in memory for this test
        old_key = settings.serper_api_key
        settings.serper_api_key = ""
        res = await search_web("test query", num_results=1)
        print(f"Result with NO KEYS: {res['status']}, error: {res.get('error')}")
        settings.serper_api_key = old_key
    else:
        print("ℹ️ Both keys might be present. Check logs for 'Attempting web search with provider'...")

    print("\n✅ Verification script finished.")

if __name__ == "__main__":
    asyncio.run(verify_search())
