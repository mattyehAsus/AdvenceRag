from advence_rag.config.settings import get_settings, Settings
import pytest

def test_get_settings():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)

def test_settings_default_values():
    """Test default values of Settings."""
    settings = Settings()
    # Assuming these are some default values from the codebase
    assert settings.chroma_collection_name == "knowledge_base"
    assert settings.log_level == "INFO"

def test_settings_override():
    """Test overriding Settings via constructor."""
    settings = Settings(log_level="DEBUG", chroma_collection_name="custom")
    assert settings.log_level == "DEBUG"
    assert settings.chroma_collection_name == "custom"
