from tenacity import retry, retry_if_exception_type, wait_fixed

from .config import settings
from .main import app

import aioredis
import aio_pika


@app.on_event("startup")
async def init_redis():
    app.state.redis = await aioredis.from_url(settings.redis_url, max_connections=20)


@app.on_event("startup")
@retry(retry=retry_if_exception_type(ConnectionError), wait=wait_fixed(2))
async def init_rabbit():
    app.state.rabbit = await aio_pika.connect_robust(settings.rabbitmq_url)


@app.on_event("shutdown")
async def close_rabbit():
    await app.state.rabbit.close()


@app.on_event("shutdown")
async def close_redis():
    await app.state.redis.close()
