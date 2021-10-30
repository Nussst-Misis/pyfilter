from pydantic import BaseSettings

__all__ = ("settings",)


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket: str
    max_workers: int = 1


settings = Settings()
