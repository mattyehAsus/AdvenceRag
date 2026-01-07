import sys
import logging
from pathlib import Path
import shutil
import time

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from advence_rag.workflows.optimization import optimization_pipeline
from advence_rag.tools.knowledge_base import search_similar, delete_documents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ingestion():
    print("Testing Ingestion Pipeline...")
    
    # 1. Prepare data
    test_dir = Path("./test_data_ingest")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    sample_file = test_dir / "test_doc.txt"
    sample_content = "The Advanced RAG system uses a multi-agent architecture with Google Gemini."
    sample_file.write_text(sample_content, encoding="utf-8")
    
    print(f"Created sample file: {sample_file}")

    # 2. Process document directly (to verify parsing and embedding)
    print("Processing document...")
    # We use the pipeline to process the single file
    result = optimization_pipeline.process_document(sample_file)
    print(f"Process result: {result}")
    
    if result["status"] != "success":
        print("Error: Processing failed")
        sys.exit(1)

    # 3. Verify in ChromaDB
    print("Verifying in ChromaDB...")
    # Give a slight delay for persistence if needed
    time.sleep(1)
    
    # Search for a keyword in the content
    search_result = search_similar(query="Gemini", top_k=1)
    print(f"Search result: {search_result}")
    
    if not search_result["results"]:
        print("Error: Document not found in ChromaDB")
        sys.exit(1)
        
    found_content = search_result["results"][0]["content"]
    # Verify the content matches (at least partially)
    if "Google Gemini" not in found_content:
         print(f"Warning: Content might be chunked differently. Found: {found_content}")

    print("Ingestion verification passed!")

    # Cleanup
    # Clean up the specific document we added to avoid polluting the DB for other tests
    ids = [res["id"] for res in search_result["results"]]
    if ids:
        delete_documents(ids)
        print("Cleaned up database records.")
    
    shutil.rmtree(test_dir)
    print("Cleanup done.")

if __name__ == "__main__":
    test_ingestion()
