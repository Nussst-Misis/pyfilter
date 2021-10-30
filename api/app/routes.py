from fastapi import APIRouter, HTTPException, Request, Depends
from aiohttp import ClientSession, ClientResponse
from pydantic import BaseModel
from io import BytesIO


from .processing import process, RecognitionResult
from .config import settings

import asyncio

router = APIRouter()


class RecognizeRequest(BaseModel):
    source: str
    prefix: str


class RecognizeResponse(BaseModel):
    code: str
    message: str


async def depends_s3(request: Request):
    async with request.state.aws_session.client("s3") as client:
        yield client


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(
    data: RecognizeRequest, request: Request, s3client=Depends(depends_s3)
):
    async with ClientSession() as session:
        async with session.get(data.source) as response:  # type: ClientResponse
            if response.status != 200:
                raise HTTPException(status_code=400, detail="Unable to download video")
            content = await response.read()

    loop = asyncio.get_running_loop()
    result: RecognitionResult = await loop.run_in_executor(
        request.state.executor, process, content
    )

    audio = BytesIO(result.audio.json().encode("utf-8"))
    video = BytesIO(result.video.json().encode("utf-8"))
    result.result_file.seek(0)

    await s3client.upload_fileobj(
        audio, settings.aws_bucket, f"{data.prefix}_audio.json"
    )
    await s3client.upload_fileobj(
        video, settings.aws_bucket, f"{data.prefix}_video.json"
    )
    await s3client.upload_fileobj(
        result.result_file, settings.aws_bucket, f"{data.prefix}_result.mp4"
    )

    return RecognizeResponse(code="ok", message="Processing complete")
