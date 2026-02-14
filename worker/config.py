from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSetting):
    # Required Variables
    openai_api_key: str

    # Optional Variables (With Defaults)
    redis_url: str = "localhost"
    redis_port: int = 6379
    qdrant_url: str = "localhost"
    qdrant_port: int = 6333
    
    # Collection Names (Hardcoded or Configurable)
    colection_wisdom: str = "wisdom"
    Collection_wire: str = "wire"
    
    # Configuration to load from .env automatically
    model_congit = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()