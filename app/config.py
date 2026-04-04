import os
from dataclasses import dataclass


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str

    openai_api_key: str

    jwt_secret: str
    jwt_alg: str
    access_ttl_min: int
    refresh_ttl_days: int

    redis_url: str
    rate_limit_enabled: bool
    rate_limit_per_minute: int


def load_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "dev").lower()
    strict = app_env in {"staging", "prod"}

    if strict:
        openai_api_key = _require("OPENAI_API_KEY")
        jwt_secret = _require("JWT_SECRET")
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        jwt_secret = os.getenv("JWT_SECRET", "change-me")

    return Settings(
        app_env=app_env,
        log_level=os.getenv("LOG_LEVEL", "INFO"),

        openai_api_key=openai_api_key,

        jwt_secret=jwt_secret,
        jwt_alg=os.getenv("JWT_ALG", "HS256"),
        access_ttl_min=int(os.getenv("ACCESS_TTL_MIN", "30")),
        refresh_ttl_days=int(os.getenv("REFRESH_TTL_DAYS", "7")),

        redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        rate_limit_enabled=_as_bool(os.getenv("RATE_LIMIT_ENABLED", "true")),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "20")),
    )


settings = load_settings()