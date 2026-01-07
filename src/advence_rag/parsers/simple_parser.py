
from pathlib import Path
from advence_rag.parsers.base import BaseParser, Document

class SimpleTextParser(BaseParser):
    """Simple text parser that just reads the file."""
    
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".log"}
    
    def supports(self, file_type: str) -> bool:
        return file_type.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: str | Path) -> list[Document]:
        path = self._ensure_path(file_path)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")
            
        return [Document(
            content=content,
            metadata={
                "parser": "simple_text",
                "file_name": path.name,
            },
            source=str(path),
            chunk_id=f"{path.stem}_full",
        )]
