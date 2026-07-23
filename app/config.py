from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    planning_llm_provider: Literal["openai", "anthropic"] = "openai"
    planning_llm_model: str = "gpt-4o-mini"
    local_llm_provider: Literal["ollama"] = "ollama"
    local_llm_model: str = "qwen2.5:3b"
    ollama_base_url: str = "http://localhost:11434"
    max_upload_size_mb: int = 25

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
