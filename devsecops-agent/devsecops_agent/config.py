"""Configuration helpers for the DevSecOps agent."""

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    github_token: str = os.getenv("GITHUB_TOKEN", "")


settings = Settings()
