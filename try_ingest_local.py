
import sys
from pathlib import Path
import logging

# Mimic clean environment
src_path = Path("src").resolve()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from advence_rag.config import get_settings
from advence_rag.utils import setup_logging
from advence_rag.parsers import ParserType

def main():
    setup_logging("DEBUG")
    print("DEBUG: Try Ingest Local Script")
    
    file_path = Path("docs/ASUS-ExpertBook-B5402-E19560_B5402CEA_B5402FEA_SM_WEB.pdf")
    parser_type = ParserType.PYMUPDF
    
    print("DEBUG: importing optimization module...")
    from advence_rag.workflows.optimization import OptimizationPipeline
    
    print("DEBUG: Instantiating OptimizationPipeline...")
    pipeline = OptimizationPipeline()
    
    print(f"DEBUG: Processing {file_path} with {parser_type}...")
    result = pipeline.process_document(file_path, parser_type)
    print(f"DEBUG: Result: {result}")
    
if __name__ == "__main__":
    main()
