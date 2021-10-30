from tenacity import retry, RetryCallState
from loguru import logger
from contextlib import AsyncExitStack
from aiohttp import ClientSession, ClientResponse
from io import BytesIO

from .models import Task, AudioResult, VideoResult
from .config import settings
from .process import process_video

import asyncio
import aio_pika
import aioredis
import aioboto3
import json


def after_log(retry_state: RetryCallState):
    logger.error(retry_state)


@retry(wait=5)
async def get_rabbit_connection() -> aio_pika.RobustConnection:
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def get_redis_connection() -> aioredis.client.Redis:
    return await aioredis.from_url(settings.redis_url, max_connections=20)


def get_boto_session() -> aioboto3.Session:
    return aioboto3.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


async def download_content(url: str) -> bytes:
    async with ClientSession() as session:
        async with session.get(url) as response:  # type: ClientResponse
            if response.status != 200:
                raise ConnectionError("Unable to download")
            return await response.read()


async def main():
    async with AsyncExitStack() as stack:
        session = get_boto_session()
        rabbit = await stack.enter_async_context(get_rabbit_connection())
        redis = await stack.enter_async_context(get_redis_connection())
        s3client = await stack.enter_async_context(session.client("s3", endpoint_url=settings.aws_endpoint))
        await worker(s3client, rabbit, redis)


@retry(wait=5, after=after_log)
async def worker(s3client, rabbit, redis):
    channel = await rabbit.channel()
    queue = await channel.declare_queue("process_video")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            message: aio_pika.IncomingMessage
            task, video, audio, result = await process_message(message)
            audio = BytesIO(audio.json().encode("utf-8"))
            video = BytesIO(video.json().encode("utf-8"))

            await s3client.upload_fileobj(
                audio, settings.aws_bucket, f"{task.message.prefix}_audio.json"
            )
            await s3client.upload_fileobj(
                video, settings.aws_bucket, f"{task.message.prefix}_video.json"
            )
            await s3client.upload_fileobj(
                result, settings.aws_bucket, f"{task.message.prefix}_result.mp4"
            )

            await redis.set(f"task.{task.task_id}", 1)


async def process_message(message) -> tuple[Task, VideoResult, AudioResult, BytesIO]:
    async with message.process():
        task = Task(**json.loads(message.body))
        content = await download_content(task.message.source)
        video, audio, result = process_video(content)
        return task, video, audio, result


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
