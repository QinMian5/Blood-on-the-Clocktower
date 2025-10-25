import os
from functools import lru_cache


class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    app_secret: str = os.getenv("APP_SECRET", "dev-secret")
    db_url: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./app.db")
    redis_url: str | None = os.getenv("REDIS_URL") or None
    user_db_path: str = os.getenv("USER_DB_PATH", "./backend/data/users.db")
    game_db_path: str = os.getenv("GAME_DB_PATH", "./backend/data/game_records.db")
    registration_codes_path: str = os.getenv(
        "REGISTRATION_CODES_PATH", "./backend/data/registration_codes.txt"
    )
    admin_secrets_path: str = os.getenv("ADMIN_SECRETS_PATH", "/etc/secrets/admin")
    cors_origins: list[str]

    def __init__(self) -> None:
        raw_origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
        if not self.cors_origins:
            self.cors_origins = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
