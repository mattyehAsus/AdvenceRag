"""Base classes for document parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class Document:
    """解析後的文檔結構。"""
    
    content: str
    """文檔內容（Markdown 格式）"""
    
    metadata: dict[str, Any] = field(default_factory=dict)
    """文檔 metadata（來源、頁數、作者等）"""
    
    source: str = ""
    """來源檔案路徑"""
    
    page_number: int | None = None
    """頁碼（如適用）"""
    
    chunk_id: str = ""
    """分塊 ID"""


@runtime_checkable
class DocumentParser(Protocol):
    """文檔解析器協議。
    
    所有解析器必須實作此協議。
    """
    
    def parse(self, file_path: str | Path) -> list[Document]:
        """解析文檔並返回 Document 列表。
        
        Args:
            file_path: 文檔路徑
            
        Returns:
            list[Document]: 解析後的文檔列表
        """
        ...
    
    def supports(self, file_type: str) -> bool:
        """檢查是否支援該檔案類型。
        
        Args:
            file_type: 檔案副檔名（如 '.pdf'）
            
        Returns:
            bool: 是否支援
        """
        ...


class BaseParser(ABC):
    """解析器基類。"""
    
    @abstractmethod
    def parse(self, file_path: str | Path) -> list[Document]:
        """解析文檔。"""
        pass
    
    @abstractmethod
    def supports(self, file_type: str) -> bool:
        """檢查支援的檔案類型。"""
        pass
    
    def _ensure_path(self, file_path: str | Path) -> Path:
        """確保路徑是 Path 物件。"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path
