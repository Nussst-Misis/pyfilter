from pydantic import BaseSettings

__all__ = ("settings", "PROCESSING_TIMEOUT")

PROCESSING_TIMEOUT = 60 * 60


class Settings(BaseSettings):
    rabbitmq_url: str
    redis_url: str


settings = Settings()
