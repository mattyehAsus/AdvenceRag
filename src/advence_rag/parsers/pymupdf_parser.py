"""PyMuPDF Parser - 輕量級 PDF 文字擷取。

最佳場景：純文字 PDF、速度優先的情況。
"""

from pathlib import Path

from advence_rag.parsers.base import BaseParser, Document


class PyMuPDFParser(BaseParser):
    """使用 pymupdf4llm 的 PDF 解析器。
    
    特點：
    - 輕量級、速度快
    - 直接輸出 LLM-ready Markdown
    - 無需外部服務
    """
    
    SUPPORTED_EXTENSIONS = {".pdf"}
    
    def __init__(self):
        """初始化解析器。"""
        try:
            import pymupdf4llm  # noqa: F401
        except ImportError:
            raise ImportError(
                "pymupdf4llm is required. Install with: pip install pymupdf4llm"
            )
    
    def supports(self, file_type: str) -> bool:
        """檢查是否支援該檔案類型。"""
        return file_type.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: str | Path) -> list[Document]:
        """解析 PDF 文檔。
        
        Args:
            file_path: PDF 檔案路徑
            
        Returns:
            list[Document]: 解析後的文檔列表（每頁一個 Document）
        """
        import pymupdf4llm
        
        path = self._ensure_path(file_path)
        
        # 使用 pymupdf4llm 轉換為 Markdown
        md_text = pymupdf4llm.to_markdown(str(path))
        
        # 如果需要按頁分割，可以使用 page_chunks
        try:
            pages = pymupdf4llm.to_markdown(str(path), page_chunks=True)
            
            documents = []
            for i, page_content in enumerate(pages, 1):
                # page_content 可能是 dict 或 str
                if isinstance(page_content, dict):
                    content = page_content.get("text", "")
                    metadata = page_content.get("metadata", {})
                else:
                    content = str(page_content)
                    metadata = {}
                
                documents.append(Document(
                    content=content,
                    metadata={
                        "parser": "pymupdf4llm",
                        "file_name": path.name,
                        **metadata,
                    },
                    source=str(path),
                    page_number=i,
                    chunk_id=f"{path.stem}_page_{i}",
                ))
            
            return documents
            
        except Exception:
            # Fallback: 返回整個文檔作為單一 Document
            return [Document(
                content=md_text,
                metadata={
                    "parser": "pymupdf4llm",
                    "file_name": path.name,
                },
                source=str(path),
                chunk_id=f"{path.stem}_full",
            )]
