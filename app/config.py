import os
from dataclasses import dataclass


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # Core app
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Security / JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-this")
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    access_token_expire_min: int = _to_int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"), 30)
    refresh_token_expire_min: int = _to_int(os.getenv("REFRESH_TOKEN_EXPIRE_MIN"), 60 * 24 * 7)

    # Rate limiting
    rate_limit_enabled: bool = _to_bool(os.getenv("RATE_LIMIT_ENABLED"), True)
    rate_limit_per_minute: int = _to_int(os.getenv("RATE_LIMIT_PER_MINUTE"), 10)

    # Integrations
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aris.db")

    # Optional toggles
    debug: bool = _to_bool(os.getenv("DEBUG"), False)

    def masked(self) -> dict:
        """Safe settings view for logs/debug endpoints."""
        return {
            "app_env": self.app_env,
            "log_level": self.log_level,
            "jwt_alg": self.jwt_alg,
            "access_token_expire_min": self.access_token_expire_min,
            "refresh_token_expire_min": self.refresh_token_expire_min,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "redis_url": self.redis_url,
            "database_url": self.database_url,
            "openai_api_key_set": bool(self.openai_api_key),
            "jwt_secret_set": bool(self.jwt_secret),
            "debug": self.debug,
        }


settings = Settings()