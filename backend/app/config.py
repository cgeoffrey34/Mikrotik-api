from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Mikrotik Management"
    database_url: str = "sqlite+aiosqlite:///./mikrotik.db"
    secret_key: str = "change-this-secret-key-in-production"
    api_prefix: str = "/api"

    # Polling interval for router stats (in seconds)
    stats_polling_interval: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
