from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./invoices.db"
    max_upload_size_mb: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
