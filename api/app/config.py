from pydantic import BaseSettings
from typing import Optional

__all__ = ("settings",)


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket: str
    aws_endpoint: Optional[str]
    max_workers: int = 1


settings = Settings()
