"""Application settings using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 找到專案根目錄的 .env 檔案
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google API
    google_api_key: str = Field(default="", description="Google API Key for Gemini")
    google_search_api_key: str = Field(default="", description="Google Custom Search API Key")
    google_search_cse_id: str = Field(default="", description="Google Custom Search Engine ID")
    serper_api_key: str = Field(default="", description="Serper.dev API Key")
    search_provider: Literal["google", "serper"] = Field(default="serper", description="Primary search provider")

    # LLM Settings
    llm_model: str = Field(default="gemini-2.5-flash-lite", description="LLM model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Embedding
    embedding_model: str = Field(default="models/text-embedding-004")

    # Chroma Vector Database
    chroma_persist_directory: Path = Field(default=Path("./data/chroma"))
    chroma_collection_name: str = Field(default="knowledge_base")

    # Rerank Model
    rerank_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Guard Agent
    guard_enabled: bool = Field(default=True)
    guard_sensitive_patterns_str: str = Field(default="", alias="guard_sensitive_patterns")

    @property
    def guard_sensitive_patterns(self) -> list[str]:
        """Convert comma-separated string to list."""
        if not self.guard_sensitive_patterns_str:
            return []
        return [p.strip() for p in self.guard_sensitive_patterns_str.split(",") if p.strip()]

    # Scheduler
    scheduler_enabled: bool = Field(default=True)
    scheduler_timezone: str = Field(default="Asia/Taipei")

    # Retrieval Settings
    retrieval_top_k: int = Field(default=10)
    rerank_top_k: int = Field(default=5)

    # Processing Settings
    max_reflection_iterations: int = Field(default=3)
    max_agent_iterations: int = Field(default=5, description="Maximum iterations between agents (e.g., writer <-> orchestrator)")

    @property
    def data_dir(self) -> Path:
        """Get the base data directory."""
        return self.chroma_persist_directory.parent

    @property
    def uploads_dir(self) -> Path:
        """Get the uploads directory."""
        path = self.data_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
