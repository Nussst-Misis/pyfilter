from pydantic import BaseSettings

__all__ = ("settings",)


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket: str
    aws_endpoint: str
    max_workers: int = 1
    rabbitmq_url: str
    redis_url: str


settings = Settings()
