from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    cache_ttl_seconds: int = 3600
    openai_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    default_model_provider: str = "openai"
    default_model_name: str = "gpt-4o-mini"
    openai_model_name: str = "gpt-4o-mini"
    gemini_model_name: str = "gemini-2.5-flash"
    groq_model_name: str = "llama-3.3-70b-versatile"
    embedding_provider: str = "openai"
    embedding_model_name: str = "text-embedding-3-small"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "procurebrain"
    qdrant_url: str = "http://localhost:6333"
    qdrant_path: str = "./data/qdrant-local"
    qdrant_api_key: str = ""
    qdrant_collection: str = "procurebrain-knowledge"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
