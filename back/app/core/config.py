from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/weread_review?charset=utf8mb4"
    weread_api_base: str = "https://i.weread.qq.com/api/agent/gateway"
    weread_skill_version: str = "1.0.3"
    auth_secret_key: str = "change-me-in-production"
    encryption_secret: str = "0123456789abcdef0123456789abcdef"
    access_token_expire_minutes: int = 60 * 24 * 14
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
