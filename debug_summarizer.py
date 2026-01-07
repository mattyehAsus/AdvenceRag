
import sys
from pathlib import Path

# Add src to path
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from advence_rag.tools.summarizer import extract_key_points

def test_summarizer():
    content = "This is a sample document for testing the RAG system. It is a multi-agent system."
    print("Extracting key points...")
    from advence_rag.config import get_settings
    settings = get_settings()
    print(f"API Key present: {bool(settings.google_api_key)}")
    if settings.google_api_key:
        print(f"API Key length: {len(settings.google_api_key)}")
    else:
        print("API KEY IS MISSING or EMPTY!")
    
    try:
        result = extract_key_points(content)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    test_summarizer()
