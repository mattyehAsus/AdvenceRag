"""Parsers module - 文檔解析器（Strategy Pattern）。

支援依情境選用不同的解析器：
- docling: 複雜 PDF（表格、圖片）
- unstructured: 多格式（DOCX, PPTX, HTML）
- pymupdf4llm: 輕量 PDF 文字擷取
"""

from enum import Enum
from typing import TYPE_CHECKING

from advence_rag.parsers.base import Document, DocumentParser

if TYPE_CHECKING:
    pass


class ParserType(Enum):
    """可用的解析器類型。"""
    
    DOCLING = "docling"
    UNSTRUCTURED = "unstructured"
    PYMUPDF = "pymupdf"
    SIMPLE = "simple"
    AUTO = "auto"


def get_parser(parser_type: ParserType = ParserType.AUTO) -> DocumentParser:
    """Parser Factory - 依情境選擇解析器。
    
    Args:
        parser_type: 解析器類型
        
    Returns:
        DocumentParser: 對應的解析器實例
        
    Raises:
        ImportError: 如果所需的解析器套件未安裝
    """
    if parser_type == ParserType.DOCLING:
        from advence_rag.parsers.docling_parser import DoclingParser
        return DoclingParser()
    
    elif parser_type == ParserType.UNSTRUCTURED:
        from advence_rag.parsers.unstructured_parser import UnstructuredParser
        return UnstructuredParser()
    
    elif parser_type == ParserType.PYMUPDF:
        from advence_rag.parsers.pymupdf_parser import PyMuPDFParser
        return PyMuPDFParser()

    elif parser_type == ParserType.SIMPLE:
        from advence_rag.parsers.simple_parser import SimpleTextParser
        return SimpleTextParser()
    
    elif parser_type == ParserType.AUTO:
        # AUTO 模式：嘗試使用最輕量的 pymupdf，如果失敗則依序嘗試其他
        for ptype in [ParserType.PYMUPDF, ParserType.UNSTRUCTURED, ParserType.DOCLING]:
            try:
                return get_parser(ptype)
            except ImportError:
                continue
        
        raise ImportError(
            "No parser available. Install at least one: "
            "pip install pymupdf4llm, pip install unstructured, or pip install docling"
        )
    
    else:
        raise ValueError(f"Unknown parser type: {parser_type}")


def detect_best_parser(file_path: str) -> ParserType:
    """根據檔案類型自動偵測最適合的解析器。
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        ParserType: 建議的解析器類型
    """
    import os
    ext = os.path.splitext(file_path)[1].lower()
    
    # PDF 檔案
    if ext == ".pdf":
        # 預設使用 pymupdf（最快），複雜 PDF 可手動指定 docling
        return ParserType.PYMUPDF
    
    # Office 文件
    if ext in [".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"]:
        return ParserType.UNSTRUCTURED
    
    # 網頁/Email
    if ext in [".html", ".htm", ".eml", ".msg"]:
        return ParserType.UNSTRUCTURED
    
    if ext in [".txt", ".md", ".log"]:
        return ParserType.SIMPLE

    # 其他：嘗試 unstructured
    return ParserType.UNSTRUCTURED


__all__ = [
    "ParserType",
    "DocumentParser",
    "Document",
    "get_parser",
    "detect_best_parser",
]
