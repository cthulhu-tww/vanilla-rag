import logging
from typing import List

from fastapi import APIRouter, Query, UploadFile, File, Form, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tortoise.exceptions import DoesNotExist

from src.server.core.middleware import LogRoute
from src.server.core.security import check_token
from src.server.schemas import common as BaseSchema, document as DocumentSchema
from src.server.service import document as DocumentService
from src.server.service import folder as FolderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/document", tags=["文档管理"], route_class=LogRoute)

ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx", "ppt", "pptx", "xls", "xlsx", "csv", ".jpg", ".jpeg", ".png"}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def allowed_file(filename: str) -> bool:
    # 判断文件扩展名是否符合要求
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/folder/add", response_model=DocumentSchema.FolderOut, summary="创建文件夹")
async def add_folder(folder: DocumentSchema.FolderIn, user=Depends(check_token)):
    try:
        folder_out = await FolderService.add_folder(folder, user)
    except ValueError as e:
        return JSONResponse(status_code=200, content={"code": 500, "msg": str(e)})
    return JSONResponse(status_code=200,
                        content={"code": 200, "data": jsonable_encoder(folder_out), "msg": "文件夹创建成功"})


@router.delete("/folder/{folder_id}", response_model=None, summary="删除文件夹")
async def delete_folder(folder_id: int):
    try:
        await FolderService.delete_folder(folder_id)
    except DoesNotExist:
        return JSONResponse(status_code=200, content={"code": 404, "msg": "文件夹未找到"})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "文件夹删除成功"})


@router.get("/folder/get_by_id/{folder_id}")
async def get_by_id(folder_id: int):
    folder = await FolderService.get_folder_by_id(folder_id)
    return JSONResponse(status_code=200, content={"code": 200, "data": jsonable_encoder(folder)})


@router.post("/uploads", summary="上传文档文件(多个)")
async def upload_document(files: List[UploadFile] = File(...), folder_id: int = Form(...)):
    document_out_list = []

    for file in files:
        if not allowed_file(file.filename):
            return JSONResponse(status_code=200, content={"code": 400, "msg": f"文件格式不支持: {file.filename}"})

        if file.size > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=200,
                content={"code": 400, "msg": f"文件大小超过限制 (20MB): {file.filename}"}
            )
        # 重置文件指针
        await file.seek(0)

        try:
            document_out = await DocumentService.upload_document(file, folder_id)
            document_out_list.append(document_out)
        except ValueError as e:
            print(e)
            return JSONResponse(status_code=200, content={"code": 500, "msg": str(e)})

    return JSONResponse(status_code=200,
                        content={"code": 200, "data": jsonable_encoder(document_out_list), "msg": "文档上传成功"})


@router.get("/list", response_model=BaseSchema.ListAll[DocumentSchema.DocumentOut],
            summary="分页查询文件夹下的文档列表")
async def get_all_documents(folder_id: int, offset: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    query = BaseSchema.QueryData(offset=offset, limit=limit)
    document_out_list = await DocumentService.get_all_documents(folder_id, query)

    return JSONResponse(status_code=200, content={"code": 200, "data": jsonable_encoder(document_out_list),
                                                  "msg": "获取文档列表成功"})


@router.delete("/{document_id}", response_model=None, summary="删除文档")
async def delete_document(document_id: int):
    try:
        await DocumentService.delete_document(document_id)
    except DoesNotExist:
        return JSONResponse(status_code=200, content={"code": 404, "msg": "文档未找到"})
    return JSONResponse(status_code=200, content={"code": 200, "msg": "文档删除成功"})


@router.get("/folders", response_model=BaseSchema.ListAll[DocumentSchema.FolderOut], summary="分页查询所有文件夹")
async def get_all_folders(offset: int = Query(1, ge=1), limit: int = Query(10, ge=1), user=Depends(check_token)):
    query = BaseSchema.QueryData(offset=offset, limit=limit)
    folders = await FolderService.get_all_folders(query, user)
    return JSONResponse(status_code=200,
                        content={"code": 200, "data": folders, "msg": "获取文件夹列表成功"})


@router.get("/all_folders_info", response_model=List[DocumentSchema.FolderWithDocumentsOut],
            summary="查询所有文件夹及其文档信息")
async def get_all_folders_and_documents(user=Depends(check_token)):
    try:
        folders_with_documents = await FolderService.get_all_folders_with_documents(user)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(status_code=200, content={"code": 500, "msg": "服务器内部错误"})
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200,
        "data": folders_with_documents,
        "msg": "获取所有文件夹及文档信息成功"
    }))


@router.post("/split_setting", summary="文件参数设置")
async def split_setting(document_setting: DocumentSchema.SplitSetting):
    try:
        await FolderService.split_setting(document_setting)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(status_code=200, content={"code": 500, "msg": "文件参数设置出错"})
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200,
        "msg": "文件参数设置成功"
    }))


@router.post("/get_document_settings", summary="获取文件参数设置")
async def get_document_settings(data: DocumentSchema.DocumentSetting):
    try:
        settings = await FolderService.get_document_settings(data.document_id, data.knowledge_id)
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200,
            "data": settings,
            "msg": "文件参数设置成功"
        }))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(status_code=200, content={"code": 500, "msg": "无法获取文件参数"})


@router.post("/analysis_document", summary="分析文档")
async def analysis_document(document_analysis: DocumentSchema.DocumentAnalysis):
    await FolderService.analysis_document(document_analysis)
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200,
        "msg": "请求成功"
    }))
