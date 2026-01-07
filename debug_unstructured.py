
from pathlib import Path
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    print("Importing unstructured...")
    from unstructured.partition.auto import partition
    print("Import successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_partition():
    file_path = "test_data/sample.txt"
    print(f"Partitioning {file_path}...")
    try:
        elements = partition(filename=file_path)
        print(f"Partition successful. Found {len(elements)} elements.")
        for el in elements:
            print(f"- {type(el).__name__}: {str(el)[:50]}")
    except Exception as e:
        print(f"Partition failed: {e}")

if __name__ == "__main__":
    test_partition()
