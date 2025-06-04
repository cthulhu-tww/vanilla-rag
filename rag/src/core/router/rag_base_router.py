import asyncio
import uuid
from typing import List

from fastapi import APIRouter, Request, UploadFile
from haystack.dataclasses import ByteStream
from starlette.responses import StreamingResponse, JSONResponse

from src.server.entity import ChatFilesModel
from src.core import rag_base
from src.core.entity.entity import Message, Params
from src.core.util import io_util
from src.core.util.io_util import CHAT_FILE_FOLDER

router = APIRouter(prefix="/api/rag_base", tags=["rag模型模块"])


@router.post("/upload_file")
async def upload_file(files: List[UploadFile]):
    async def process_file(file: UploadFile):
        filename = file.filename
        data = await file.read()
        content_type = file.content_type
        path = await io_util.upload(data=data, filename=filename, folder_name=CHAT_FILE_FOLDER)

        content = ''
        if not content_type.startswith('image'):
            byte_stream = ByteStream(data=data, mime_type=content_type,
                                     meta={"file_name": filename})

            r = await rag_base.analysis_pipe().run_async({"file_type_router": {
                "sources": [byte_stream]}})
            doc = r['doc_joiner']['documents'][0]
            content = doc.content

        return ChatFilesModel(
            file_name=filename,
            mime_type=content_type,
            size=round(file.size / 1024, 2),
            content=content,
            uuid=uuid.uuid4().__str__(),
            file_path=path,
        )

    tasks = [process_file(file) for file in files]
    objs = await asyncio.gather(*tasks)

    await ChatFilesModel.bulk_create(objs)

    return JSONResponse(status_code=200, content={"code": 200, "msg": "success", "data": [{
        "uuid": obj.uuid,
        "filename": obj.file_name,
    } for obj in objs]})


@router.post("/rag_chat_stream")
async def rag_chat_stream(context: list[Message], params: Params,
                          request: Request):
    return StreamingResponse(
        rag_base.router(context=context, params=params, request=request),
        media_type="application/json")
