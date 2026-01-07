
import sys
from pathlib import Path

# Add src to path just in case, though I'll try to use the installed package or local path
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from advence_rag.config import get_settings
    import chromadb
except ImportError:
    print("Could not import advence_rag. Make sure dependencies are installed and you are running with 'uv run'.")
    sys.exit(1)

def verify():
    settings = get_settings()
    print(f"Persist Directory: {settings.chroma_persist_directory}")
    print(f"Collection Name: {settings.chroma_collection_name}")
    
    try:
        client = chromadb.PersistentClient(path=str(settings.chroma_persist_directory))
        collection = client.get_collection(name=settings.chroma_collection_name)
        
        count = collection.count()
        print(f"Total documents in collection: {count}")
        
        if count > 0:
            results = collection.peek(limit=3)
            print("\nFirst 3 documents:")
            for i, doc in enumerate(results['documents']):
                print(f"[{i}] ID: {results['ids'][i]}")
                print(f"    Metadata: {results['metadatas'][i]}")
                print(f"    Content (snippet): {doc[:100]}...")
        else:
            print("Collection is empty.")
            
    except Exception as e:
        print(f"Error accessing ChromaDB: {e}")

if __name__ == "__main__":
    verify()
