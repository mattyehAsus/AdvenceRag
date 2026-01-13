from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from advence_rag.domain.entities import Document
from advence_rag.domain.interfaces import KnowledgeBaseRepository
from advence_rag.parsers import get_parser, detect_best_parser, ParserType

logger = logging.getLogger("advence_rag")

class IngestDocumentUseCase:
    """Use case for ingesting documents into the knowledge base."""
    
    def __init__(self, kb_repo: KnowledgeBaseRepository):
        self.kb_repo = kb_repo

    def execute(
        self, 
        file_path: str | Path, 
        parser_type: ParserType = ParserType.AUTO
    ) -> Dict[str, Any]:
        """Parse and ingest a document."""
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "error": f"File not found: {path}"}
            
        if parser_type == ParserType.AUTO:
            parser_type = detect_best_parser(str(path))
            
        try:
            parser = get_parser(parser_type)
            # Existing parsers return list of advence_rag.parsers.base.Document
            # Which is luckily compatible (or needs minor mapping if we want strict Domain)
            # Let's map for future safety.
            raw_docs = parser.parse(path)
            
            domain_docs = [
                Document(
                    content=rd.content,
                    metadata=rd.metadata,
                    source=rd.source,
                    page_number=rd.page_number,
                    chunk_id=rd.chunk_id
                ) for rd in raw_docs
            ]
            
            return self.kb_repo.add_documents(domain_docs)
            
        except Exception as e:
            logger.error(f"Ingestion failed for {path}: {e}")
            return {"status": "error", "error": str(e)}
