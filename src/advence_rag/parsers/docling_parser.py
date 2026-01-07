"""Docling Parser - 複雜 PDF 解析。

最佳場景：含表格、圖片、多欄排版的複雜 PDF。
"""

from pathlib import Path

from advence_rag.parsers.base import BaseParser, Document


class DoclingParser(BaseParser):
    """使用 Docling 的 PDF 解析器。
    
    特點：
    - 最佳結構保留
    - 表格擷取
    - 圖片偵測
    - 多欄排版支援
    """
    
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".html"}
    
    def __init__(self):
        """初始化解析器。"""
        try:
            from docling.document_converter import DocumentConverter  # noqa: F401
        except ImportError:
            raise ImportError(
                "docling is required. Install with: pip install docling"
            )
    
    def supports(self, file_type: str) -> bool:
        """檢查是否支援該檔案類型。"""
        return file_type.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: str | Path) -> list[Document]:
        """解析文檔。
        
        Args:
            file_path: 文檔路徑
            
        Returns:
            list[Document]: 解析後的文檔列表
        """
        from docling.document_converter import DocumentConverter
        
        path = self._ensure_path(file_path)
        
        # 使用 Docling 轉換
        converter = DocumentConverter()
        result = converter.convert(str(path))
        
        # 轉換為 Markdown
        md_content = result.document.export_to_markdown()
        
        # Docling 提供結構化內容，可以依章節分割
        documents = []
        
        # 嘗試按章節分割
        try:
            sections = self._split_by_sections(md_content)
            for i, section in enumerate(sections):
                documents.append(Document(
                    content=section["content"],
                    metadata={
                        "parser": "docling",
                        "file_name": path.name,
                        "section_title": section.get("title", ""),
                    },
                    source=str(path),
                    chunk_id=f"{path.stem}_section_{i}",
                ))
        except Exception:
            # Fallback: 返回完整文檔
            documents.append(Document(
                content=md_content,
                metadata={
                    "parser": "docling",
                    "file_name": path.name,
                },
                source=str(path),
                chunk_id=f"{path.stem}_full",
            ))
        
        return documents
    
    def _split_by_sections(self, content: str) -> list[dict]:
        """按 Markdown 標題分割內容。"""
        import re
        
        # 按一級或二級標題分割
        pattern = r"(?=^#{1,2}\s+.+$)"
        parts = re.split(pattern, content, flags=re.MULTILINE)
        
        sections = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 擷取標題
            title_match = re.match(r"^(#{1,2})\s+(.+)$", part, re.MULTILINE)
            title = title_match.group(2) if title_match else ""
            
            sections.append({
                "title": title,
                "content": part,
            })
        
        return sections if sections else [{"title": "", "content": content}]
