from fastapi import APIRouter, Depends, Query
from fastapi import Request
from fastapi.responses import JSONResponse

from src.server.core.security import check_token
from src.server.schemas.chat_history import ChatHistoryIn, ChatHistoryContentOut, ChatHistoryTitleOut
from src.server.schemas.common import ListAll, QueryData
from src.server.service import chat as ChatHistoryService

router = APIRouter(prefix="/api/chat", tags=["对话聊天模块"])


@router.post("/", summary="创建聊天记录")
async def create_chat_history(chat_history: ChatHistoryIn, request: Request, user=Depends(check_token)):
    try:
        r = await ChatHistoryService.create_chat_history(chat_history, user.id, request)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 500, "msg": str(e)})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "聊天记录创建成功", "data": r})


@router.get("/title_list", response_model=ListAll[ChatHistoryTitleOut], summary="分页查询聊天记录标题")
async def get_chat_history_titles(offset: int = Query(1, ge=1), limit: int = Query(10, ge=1),
                                  user=Depends(check_token)):
    query = QueryData(offset=offset, limit=limit)
    try:
        chat_history_titles = await ChatHistoryService.get_chat_history_titles(user.id, query)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 404, "msg": str(e)})
    return JSONResponse(status_code=200,
                        content={"code": 200, "data": chat_history_titles.dict(), "msg": "获取聊天记录标题成功"})


@router.get("/content/{record_id}", response_model=ChatHistoryContentOut, summary="获取聊天记录内容")
async def get_chat_history_content(record_id: int):
    try:
        content_out = await ChatHistoryService.get_chat_history_content(record_id)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 404, "msg": str(e)})
    return JSONResponse(status_code=200,
                        content={"code": 200, "data": content_out.dict(), "msg": "获取聊天记录内容成功"})


@router.delete("/{record_id}", response_model=None, summary="删除聊天记录")
async def delete_chat_history(record_id: int):
    try:
        await ChatHistoryService.delete_chat_history(record_id)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 404, "msg": str(e)})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "聊天记录删除成功"})


@router.get("/clear", response_model=None, summary="清空聊天记录")
async def clear(user=Depends(check_token)):
    try:
        await ChatHistoryService.clear(user.id)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 404, "msg": str(e)})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "清空记录成功"})


@router.post("/export", response_model=None)
async def export(chat_history: ChatHistoryIn):
    return await ChatHistoryService.export(chat_history.export_type, chat_history.message_content)


@router.post("/update_title", response_model=None, summary="清空聊天记录")
async def clear(chat_history: ChatHistoryIn):
    try:
        await ChatHistoryService.update_title(chat_history)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 404, "msg": str(e)})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "修改成功"})
