"""
Centralized configuration — loaded once from environment variables.
Every other module imports `settings` from here instead of reading os.environ directly.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Groq ─────────────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Neon Postgres ────────────────────────────────────
    neon_database_url: str = ""

    # ── Redis (Upstash REST API) ─────────────────────────
    redis_url: str = ""
    upstash_redis_rest_token: str = ""

    # ── Rate Limiting ────────────────────────────────────
    rate_limit_max_requests: int = 25
    rate_limit_window_seconds: int = 60

    # ── App ──────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def async_database_url(self) -> str:
        """
        Convert the Neon connection string to asyncpg-compatible format.
        - postgresql:// → postgresql+asyncpg://
        - Remove channel_binding param (not supported by asyncpg)
        - Convert sslmode=require → ssl=require
        """
        url = self.neon_database_url
        if not url:
            return url

        # Swap driver prefix
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Remove channel_binding (asyncpg doesn't support it)
        url = url.replace("&channel_binding=require", "")
        url = url.replace("?channel_binding=require&", "?")
        url = url.replace("?channel_binding=require", "")

        # asyncpg uses 'ssl' not 'sslmode'
        url = url.replace("sslmode=require", "ssl=require")

        return url

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
