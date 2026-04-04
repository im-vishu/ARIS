import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


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


def _to_list(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    debug: bool = _to_bool(os.getenv("DEBUG"), False)

    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-this")
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    access_token_expire_min: int = _to_int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"), 30)
    refresh_token_expire_min: int = _to_int(os.getenv("REFRESH_TOKEN_EXPIRE_MIN"), 10080)

    rate_limit_enabled: bool = _to_bool(os.getenv("RATE_LIMIT_ENABLED"), True)
    rate_limit_per_minute: int = _to_int(os.getenv("RATE_LIMIT_PER_MINUTE"), 20)

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aris.db")

    cors_origins: list[str] = field(
        default_factory=lambda: _to_list(os.getenv("CORS_ORIGINS"), ["*"])
    )
    allowed_hosts: list[str] = field(
        default_factory=lambda: _to_list(os.getenv("ALLOWED_HOSTS"), ["*"])
    )

    db_pool_size: int = _to_int(os.getenv("DB_POOL_SIZE"), 5)
    db_max_overflow: int = _to_int(os.getenv("DB_MAX_OVERFLOW"), 10)

    def masked(self) -> dict:
        return {
            "app_env": self.app_env,
            "log_level": self.log_level,
            "debug": self.debug,
            "jwt_alg": self.jwt_alg,
            "access_token_expire_min": self.access_token_expire_min,
            "refresh_token_expire_min": self.refresh_token_expire_min,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "redis_url": self.redis_url,
            "database_url": self.database_url,
            "openai_api_key_set": bool(self.openai_api_key),
            "jwt_secret_set": bool(self.jwt_secret),
            "cors_origins": self.cors_origins,
            "allowed_hosts": self.allowed_hosts,
            "db_pool_size": self.db_pool_size,
            "db_max_overflow": self.db_max_overflow,
        }


settings = Settings()

if settings.app_env in {"staging", "prod"}:
    if len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be >= 32 characters in staging/prod")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required in staging/prod")
    if settings.cors_origins == ["*"]:
        raise RuntimeError("CORS_ORIGINS must not be '*' in staging/prod")
    if settings.allowed_hosts == ["*"]:
        raise RuntimeError("ALLOWED_HOSTS must not be '*' in staging/prod")