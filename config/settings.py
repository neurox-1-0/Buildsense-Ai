from functools import lru_cache
import secrets
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    flask_env: str = "development"
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = True

    mongodb_uri: str = ""
    mongodb_database: str = "buildsense_ai"
    use_memory_db: bool = True

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    youtube_api_key: str = ""
    google_maps_api_key: str = ""
    firecrawl_api_key: str = ""

    request_timeout_seconds: int = 15
    max_source_items: int = 30
    min_evidence_items: int = 3
    min_external_tools: int = 3
    min_analysis_confidence: float = 0.55
    max_graph_retries: int = 2
    max_controller_cycles: int = 24
    max_tool_calls: int = 12
    max_execution_seconds: int = 180
    enable_ai_controller: bool = True
    enable_demo_data: bool = False
    allow_private_source_urls: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
