import logging
import os
import time
import uuid
from typing import Callable

import jwt
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

from src.server.core.security import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)


class LogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            if request.headers.get('authorization') is not None:
                token = request.headers.get('authorization').replace('Bearer ', '')
            else:
                try:
                    token = request.cookies['token']
                except Exception as e:
                    return JSONResponse(status_code=200, content={"code": 403, "msg": "认证失败"})

            if token is None:
                return JSONResponse(status_code=200, content={"code": 403, "msg": "认证失败"})

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            except Exception as e:
                logger.error(e)
                return JSONResponse(status_code=200, content={"code": 403, "msg": "认证失败"})

            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
            logger.info(
                f"{request_id} Request Log {request.client} {request.method} {request.url} {request.headers}\n {await request.body()}")
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            if isinstance(response, FileResponse):
                # 文件类型响应特殊处理
                log_data = {
                    "type": "file_response",
                    "status_code": response.status_code,
                    "file_path": str(response.path),
                    "filename": response.headers.get('content-disposition', '').split('filename=')[-1],
                    "size": f"{os.path.getsize(response.path) / 1024:.2f}KB" if os.path.exists(
                        response.path) else "unknown"
                }
                logger.info(f"{request_id} File Response | {log_data}")
            elif isinstance(response, StreamingResponse):
                # 流式响应基础信息
                logger.info(
                    f"{request_id} Streaming Response\n"
                    f"Status: {response.status_code}\n"
                    f"Headers: {dict(response.headers)}\n"
                    f"Duration: {duration:.3f}s"
                )
            elif isinstance(response, Response):
                # 处理普通响应
                response_body = response.body.decode('utf-8')
                logger.info(
                    f"{request_id} Response\n"
                    f"Status: {response.status_code}\n"
                    f"Headers: {dict(response.headers)}\n"
                    f"Body: {response_body}...\n"
                    f"Duration: {duration:.3f}s"
                )

            return response

        return custom_route_handler


middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]
