import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    # --- General ---
    APP_NAME: str = "HPMS - Family Shopping Decision System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    API_V1_PREFIX: str = "/api/v1"

    # --- MySQL ---
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "hpms"
    MYSQL_PASSWORD: str = "hpms_password"
    MYSQL_DATABASE: str = "hpms"
    DATABASE_URL: str | None = None

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    # --- Redis ---
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url

    # --- Meilisearch ---
    MEILISEARCH_HOST: str = "http://meilisearch:7700"
    MEILISEARCH_API_KEY: str = "hpms_master_key"
    MEILISEARCH_INDEX: str = "products"

    # --- Alibaba Cloud OSS ---
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
    OSS_BUCKET_NAME: str = "hpms-files"
    OSS_REGION: str = "cn-hangzhou"

    # --- Alibaba Cloud OCR ---
    OCR_ACCESS_KEY_ID: str = ""
    OCR_ACCESS_KEY_SECRET: str = ""
    OCR_ENDPOINT: str = "ocr.cn-hangzhou.aliyuncs.com"

    # --- Celery ---
    CELERY_BEAT_SCHEDULE_ENABLED: bool = True
    PRICE_SCRAPE_INTERVAL_HOURS: int = 4
    PRICE_SCRAPE_HOURS: str = "9,13,18,23"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080,http://localhost"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
