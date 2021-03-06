from tenacity import retry, RetryCallState, wait_fixed
from aiohttp import ClientSession, ClientResponse
from concurrent.futures import ProcessPoolExecutor
from contextlib import AsyncExitStack
from loguru import logger
from io import BytesIO

from .models import Task, AudioResult, VideoResult
from .process import process_video
from .config import settings

import asyncio
import aio_pika
import aioredis
import aioboto3
import json


def after_log(retry_state: RetryCallState):
    logger.error(retry_state)


@retry(wait=wait_fixed(5))
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
        rabbit = await stack.enter_async_context(await get_rabbit_connection())
        redis = await stack.enter_async_context(await get_redis_connection())
        s3client = await stack.enter_async_context(
            session.client("s3", endpoint_url=settings.aws_endpoint)
        )
        executor = ProcessPoolExecutor(max_workers=1)
        await worker(s3client, rabbit, redis, executor)


@retry(wait=wait_fixed(5), after=after_log)
@logger.catch
async def worker(s3client, rabbit, redis, executor):
    channel = await rabbit.channel()
    queue = await channel.declare_queue("process_video")

    async with queue.iterator() as queue_iter:
        logger.info("Consuming incoming messages.")
        async for message in queue_iter:
            message: aio_pika.IncomingMessage
            task, video, audio, result = await process_message(message, executor)
            audio = BytesIO(audio.json().encode("utf-8"))
            video = BytesIO(video.json().encode("utf-8"))
            result = BytesIO(result)
            logger.info("Processing complete, uploading")
            await s3client.upload_fileobj(
                audio, settings.aws_bucket, f"{task.message.prefix}_audio.json"
            )
            await s3client.upload_fileobj(
                video, settings.aws_bucket, f"{task.message.prefix}_video.json"
            )
            await s3client.upload_fileobj(
                result, settings.aws_bucket, f"{task.message.prefix}_result.mp4"
            )

            logger.info(f"Task '{task.task_id}' completed.")

            await redis.set(f"task.{task.task_id}", 1)


async def process_message(message, executor) -> tuple[Task, VideoResult, AudioResult, bytes]:
    async with message.process():
        task = Task(**json.loads(message.body))
        logger.info(f"Processing task '{task.task_id}'")
        content = await download_content(task.message.source)
        video, audio, result = await loop.run_in_executor(executor, process_video, content)
        return task, video, audio, result


if __name__ == "__main__":
    logger.info("Starting worker.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
