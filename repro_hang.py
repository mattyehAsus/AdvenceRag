
import sys
from pathlib import Path
import logging

# Mimic clean environment
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from advence_rag.config import get_settings
from advence_rag.utils import setup_logging
from advence_rag.parsers import ParserType, get_parser

def main():
    setup_logging("DEBUG")
    print("DEBUG: Mimic CLI start")
    
    file_path = Path("test_data/sample.txt")
    parser_type = ParserType.UNSTRUCTURED
    
    print("DEBUG: importing optimization_pipeline...")
    from advence_rag.workflows.optimization import optimization_pipeline
    
    print(f"DEBUG: Processing {file_path}...")
    result = optimization_pipeline.process_document(file_path, parser_type)
    print(f"DEBUG: Result: {result}")
    
if __name__ == "__main__":
    main()
