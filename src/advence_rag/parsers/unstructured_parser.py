"""Unstructured Parser - 多格式文檔解析。

最佳場景：DOCX, PPTX, HTML, Email 等多樣化格式。
"""

from pathlib import Path

from advence_rag.parsers.base import BaseParser, Document


class UnstructuredParser(BaseParser):
    """使用 Unstructured-IO 的多格式解析器。
    
    特點：
    - 支援多種檔案格式
    - 元素級別分割
    - 企業級文檔處理
    """
    
    SUPPORTED_EXTENSIONS = {
        ".pdf", ".docx", ".doc", ".pptx", ".ppt",
        ".xlsx", ".xls", ".html", ".htm",
        ".eml", ".msg", ".txt", ".md", ".rst",
        ".xml", ".json", ".csv",
    }
    
    def __init__(self):
        """初始化解析器。"""
        try:
            from unstructured.partition.auto import partition  # noqa: F401
        except ImportError:
            raise ImportError(
                "unstructured is required. Install with: "
                "pip install 'unstructured[all-docs]'"
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
        from unstructured.partition.auto import partition
        
        path = self._ensure_path(file_path)
        
        # 使用 unstructured 解析
        elements = partition(filename=str(path))
        
        # 按元素類型組織文檔
        documents = []
        current_section = []
        current_title = ""
        
        for element in elements:
            element_type = type(element).__name__
            text = str(element)
            
            # Title 元素開始新的 section
            if element_type == "Title":
                # 保存前一個 section
                if current_section:
                    documents.append(self._create_document(
                        content="\n\n".join(current_section),
                        title=current_title,
                        path=path,
                        chunk_idx=len(documents),
                    ))
                current_section = [f"# {text}"]
                current_title = text
            else:
                # 根據元素類型格式化
                formatted = self._format_element(element_type, text)
                if formatted:
                    current_section.append(formatted)
        
        # 保存最後一個 section
        if current_section:
            documents.append(self._create_document(
                content="\n\n".join(current_section),
                title=current_title,
                path=path,
                chunk_idx=len(documents),
            ))
        
        # 如果沒有識別到 sections，返回完整文檔
        if not documents:
            full_content = "\n\n".join(str(e) for e in elements)
            documents.append(Document(
                content=full_content,
                metadata={
                    "parser": "unstructured",
                    "file_name": path.name,
                    "element_count": len(elements),
                },
                source=str(path),
                chunk_id=f"{path.stem}_full",
            ))
        
        return documents
    
    def _format_element(self, element_type: str, text: str) -> str:
        """根據元素類型格式化文字。"""
        if not text.strip():
            return ""
        
        formatters = {
            "NarrativeText": lambda t: t,
            "ListItem": lambda t: f"- {t}",
            "Table": lambda t: f"\n{t}\n",
            "FigureCaption": lambda t: f"*{t}*",
            "Header": lambda t: f"## {t}",
            "Footer": lambda t: f"---\n{t}",
        }
        
        formatter = formatters.get(element_type, lambda t: t)
        return formatter(text)
    
    def _create_document(
        self,
        content: str,
        title: str,
        path: Path,
        chunk_idx: int,
    ) -> Document:
        """建立 Document 物件。"""
        return Document(
            content=content,
            metadata={
                "parser": "unstructured",
                "file_name": path.name,
                "section_title": title,
            },
            source=str(path),
            chunk_id=f"{path.stem}_section_{chunk_idx}",
        )
