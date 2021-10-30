from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from aio_pika import RobustConnection, Message
from aioredis.client import Redis
from enum import IntEnum

from .config import PROCESSING_TIMEOUT

import json
import uuid

router = APIRouter()


class RecognizeRequest(BaseModel):
    source: str
    prefix: str


class RecognizeResponse(BaseModel):
    code: str
    message: dict


class TaskStatus(IntEnum):
    PROCESSING = 0
    COMPLETED = 1


class StatusResponse(BaseModel):
    status: TaskStatus
    detail: str


def depends_redis(request: Request) -> Redis:
    return request.state.redis


def depends_rabbit(request: Request) -> RobustConnection:
    return request.state.rabbit


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(
        data: RecognizeRequest,
        redis: Redis = Depends(depends_redis),
        rabbit: RobustConnection = Depends(depends_rabbit)
):
    task_id = str(uuid.uuid4())
    channel = await rabbit.channel()

    await channel.declare_queue("process_video")
    await channel.default_exchange.publish(
        Message(
            body=json.dumps(
                {
                    "task_id": task_id,
                    "message": data.dict()
                }
            ).encode("utf-8"),
            expiration=PROCESSING_TIMEOUT
        ),
        routing_key="process_video",
    )

    await redis.set(f"task.{task_id}", 0)
    await redis.expire(f"task.{task_id}", PROCESSING_TIMEOUT)

    return RecognizeResponse(code="ok", message={"task_id": task_id})


@router.get("/task_status", response_model=StatusResponse)
async def task_status(task_id: int, redis: Redis = Depends(depends_redis)):
    status = await redis.get(f"task.{task_id}")
    if status == TaskStatus.PROCESSING:
        return StatusResponse(
            status=status,
            detail="In progress."
        )
    elif status == TaskStatus.COMPLETED:
        return StatusResponse(
            status=status,
            detail="Completed."
        )
    else:
        raise HTTPException(detail="Task expired or does not exists.", status_code=400)
