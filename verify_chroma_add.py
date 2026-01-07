
import sys
from pathlib import Path
import logging

# Mimic clean environment
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from advence_rag.tools.knowledge_base import add_documents
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def main():
    print("Testing add_documents...")
    try:
        result = add_documents(["Test content"], metadatas=[{"source": "test"}], ids=["test_id_1"])
        print(f"Result: {result}")
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    main()
