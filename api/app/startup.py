from concurrent.futures import ProcessPoolExecutor

from .config import settings
from .main import app

import aioboto3


@app.on_event("startup")
async def init_process_pool():
    app.state.executor = ProcessPoolExecutor(max_workers=1)


@app.on_event("shutdown")
async def close_process_pool():
    app.state.executor.shutdown(wait=True)


@app.on_event("startup")
async def init_aws():
    app.state.aws_session = aioboto3.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
