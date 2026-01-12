import pytest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data (Chroma, BM25)."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="advence_rag_test_"))
    yield tmp_dir
    shutil.rmtree(tmp_dir)

@pytest.fixture
def mock_settings(test_data_dir):
    """Provide settings with temporary paths for testing."""
    from advence_rag.config.settings import Settings
    
    # Mock settings to use the temporary directory
    settings = Settings(
        chroma_persist_directory=str(test_data_dir / "chroma"),
        chroma_collection_name="test_collection",
        log_level="ERROR"
    )
    return settings

@pytest.fixture(autouse=True)
def patch_settings(monkeypatch, mock_settings):
    """Automatically patch get_settings to return mock_settings during tests."""
    import advence_rag.config
    import advence_rag.tools.knowledge_base
    
    monkeypatch.setattr("advence_rag.config.get_settings", lambda: mock_settings)
    # Also patch where it's already imported
    monkeypatch.setattr("advence_rag.tools.knowledge_base.settings", mock_settings)

@pytest.fixture
def sample_docs():
    """Provide a set of sample documents for testing."""
    return [
        "Advence RAG is a multi-agent system.",
        "It uses Google ADK for coordination.",
        "Chroma is used for vector storage.",
        "BM25 provides keyword matching capabilities."
    ]

@pytest.fixture
def sample_ids():
    """Provide IDs for sample documents."""
    return [f"test_id_{i}" for i in range(4)]

@pytest.fixture
def sample_metadatas():
    """Provide metadata for sample documents."""
    return [{"source": "test_suite"} for _ in range(4)]

@pytest.fixture
def temp_file(tmp_path):
    """Fixture to create a temporary file with custom content."""
    def _create_file(filename, content="test"):
        p = tmp_path / filename
        p.write_text(content)
        return p
    return _create_file

@pytest.fixture
def populated_knowledge_base(sample_docs, sample_ids, sample_metadatas):
    """Fixture that adds sample documents to the knowledge base and returns the IDs."""
    from advence_rag.tools.knowledge_base import add_documents
    add_documents(sample_docs, ids=sample_ids, metadatas=sample_metadatas)
    return sample_ids
