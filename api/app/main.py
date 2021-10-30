from fastapi import FastAPI
from .routes import router

__all__ = ("app",)

app = FastAPI(title="Zber Filter")

from .startup import *  # noqa

app.include_router(router)
