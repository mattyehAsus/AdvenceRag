"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "What is RAG and how does it work?"


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "content": "RAG stands for Retrieval-Augmented Generation.",
            "metadata": {"source": "test"},
        },
        {
            "content": "RAG combines retrieval and generation for better answers.",
            "metadata": {"source": "test"},
        },
    ]
