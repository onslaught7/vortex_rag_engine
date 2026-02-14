from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSetting):
    # Required Variables
    OPENAI_API_KEY: str

    # Optional Variables (With Defaults)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # Collection Names (Hardcoded or Configurable)
    COLLECTION_WISDOM: str = "wisdom"
    COLLECTION_WIRE: str = "wire"
    
    # Configuration to load from .env automatically
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()