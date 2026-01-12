import sys
from unittest.mock import MagicMock, patch

# Mock modules that might be missing
mock_docling = MagicMock()
mock_pymupdf = MagicMock()
sys.modules["docling"] = mock_docling
sys.modules["docling.document_converter"] = mock_docling.document_converter
sys.modules["pymupdf4llm"] = mock_pymupdf

from advence_rag.parsers import detect_best_parser, ParserType, get_parser
from advence_rag.parsers.simple_parser import SimpleTextParser
from advence_rag.parsers.docling_parser import DoclingParser
from advence_rag.parsers.pymupdf_parser import PyMuPDFParser

def test_detect_best_parser():
    """Test parser selection logic based on file extensions."""
    assert detect_best_parser("test.txt") == ParserType.SIMPLE
    assert detect_best_parser("test.md") == ParserType.SIMPLE
    assert detect_best_parser("test.pdf") == ParserType.PYMUPDF
    assert detect_best_parser("test.docx") == ParserType.UNSTRUCTURED
    assert detect_best_parser("test.unknown") == ParserType.UNSTRUCTURED

def test_simple_parser_parse(temp_file):
    """Test SimpleTextParser with a plain text file."""
    content = "Hello, this is a test document."
    f = temp_file("test.txt", content)
    
    parser = SimpleTextParser()
    docs = parser.parse(f)
    
    assert len(docs) == 1
    assert docs[0].content == content
    assert docs[0].metadata["file_name"] == "test.txt"

def test_docling_parser_mocked(temp_file):
    """Test DoclingParser with a mocked underlying library."""
    mock_converter_cls = mock_docling.document_converter.DocumentConverter
    mock_converter = mock_converter_cls.return_value
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Mocked Markdown Content"
    mock_converter.convert.return_value = mock_result
    
    f = temp_file("test.pdf", "dummy")
    parser = DoclingParser()
    docs = parser.parse(f)
    
    assert len(docs) >= 1
    assert "Mocked Markdown Content" in docs[0].content
    assert docs[0].metadata["file_name"] == "test.pdf"
    mock_converter.convert.assert_called_once()

def test_pymupdf_parser_mocked(temp_file):
    """Test PyMuPDFParser with a mocked underlying library."""
    # First call to to_markdown is for fallback md_text (line 49)
    # Second call is for pages (line 53)
    mock_pymupdf.to_markdown.side_effect = ["Mocked MD Result", ["Page 1 Content"]]
    
    f = temp_file("test.pdf", "dummy")
    parser = PyMuPDFParser()
    docs = parser.parse(f)
    
    assert len(docs) == 1
    assert docs[0].content == "Page 1 Content"
    assert docs[0].metadata["file_name"] == "test.pdf"
    assert mock_pymupdf.to_markdown.call_count == 2
