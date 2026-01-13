from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

@dataclass
class Document:
    """Core document entity."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None

@dataclass
class SearchResult:
    """Domain search result entity."""
    content: str
    metadata: Dict[str, Any]
    id: str
    score: float
    source: Optional[str] = None
    page_number: Optional[int] = None
