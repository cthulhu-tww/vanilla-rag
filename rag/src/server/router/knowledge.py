import uuid
from typing import List

from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi import Request
from tortoise.exceptions import DoesNotExist

from src.server.core.security import check_token
from src.server.schemas import common as BaseSchema, knowledge as KnowledgeSchema
from src.server.service import document as DocumentService
from src.server.service import knowledge as KnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["知识库管理"])


@router.post("/add", summary="创建知识库")
async def add_knowledge(knowledge: KnowledgeSchema.KnowledgeIn, request: Request, user=Depends(check_token)):
    uuid_str = uuid.uuid1().__str__()
    uuid_str = uuid_str.replace("-", "_")
    index_name = f"index_{uuid_str}"
    try:
        knowledge.index_name = index_name
        await request.app.state.milvus_manager.create_collection(index_name)
        knowledge_out = await KnowledgeService.add_knowledge(knowledge, user)
        return knowledge_out
    except Exception as e:
        await request.app.state.milvus_manager.drop_collection(index_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/list", summary="分页查询知识库列表")
async def getAllKnowledge(offset: int = Query(1, ge=1), limit: int = Query(10, ge=1), user=Depends(check_token)):
    query = BaseSchema.QueryData(offset=offset, limit=limit)
    knowledge_out_list = await KnowledgeService.getAllKnowledge(query, user)
    return knowledge_out_list


@router.get("/get_knowledge/{knowledge_id}", response_model=KnowledgeSchema.KnowledgeOut,
            summary="根据知识库Id查询知识库信息")
async def getKnowledge(knowledge_id: int):
    try:
        knowledge_out = await KnowledgeService.getKnowledge(knowledge_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库未找到")
    return knowledge_out


@router.put("/update_knowledge/{knowledge_id}", response_model=KnowledgeSchema.KnowledgeOut, summary="修改知识库")
async def updateKnowledge(knowledge_id: int, knowledge: KnowledgeSchema.KnowledgeIn):
    try:
        knowledge_out = await KnowledgeService.updateKnowledge(knowledge_id, knowledge)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库未找到")
    return knowledge_out


@router.delete("/delete_knowledge/{knowledge_id}", response_model=None, summary="删除知识库")
async def delete_knowledge(knowledge_id: int, request: Request):
    try:
        await KnowledgeService.delete_knowledge(knowledge_id, request.app.state.milvus_manager)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"message": "知识库删除成功"}


# 根据知识库查询文档信息
@router.get("/documents",
            summary="根据知识库查询文档信息")
async def get_documents_by_knowledge(knowledge_id: int, offset: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    documents = await DocumentService.get_documents_by_knowledge(knowledge_id, offset, limit)
    return documents


# 删除某个知识库下的多个文档
@router.delete("/documents/{knowledge_id}", response_model=None, summary="删除知识库下的文档")
async def delete_documents_by_knowledge(knowledge_id: int, document_ids: List[int], request: Request):
    await DocumentService.delete_documents_by_knowledge(knowledge_id, document_ids, request)
    return {"message": "删除知识库下的文档成功"}


# 保存知识库下的单个或多个文档
@router.post("/documents/{knowledge_id}", summary="保存知识库下的文档")
async def save_documents_to_knowledge(knowledge_id: int, document_ids: List[int]):
    await DocumentService.save_documents_to_knowledge(knowledge_id, document_ids)
    return {"message": "保存文档到知识库成功"}
