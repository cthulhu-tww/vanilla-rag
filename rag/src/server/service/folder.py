import asyncio
import logging
from typing import List

from fastapi import HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from src.core.components.analysis_task import VectorTask, AnalysisTask
from src.core.util import io_util
from src.server.entity import FolderModel, DocumentModel, KnowledgeDocumentModel, KnowledgeModel
from src.server.schemas import common as BaseSchema
from src.server.schemas.common import QueryData
from src.server.schemas.document import FolderIn, FolderOut, FolderWithDocumentsOut, DocumentBasic, \
    DocumentAnalysis, \
    SplitSetting, FolderSimple
from src.server.service.document import Document_Pydantic

logger = logging.getLogger(__name__)

# 创建 Pydantic 模型转换器
Folder_Pydantic = pydantic_model_creator(FolderModel, name="Folder")
FolderIn_Pydantic = pydantic_model_creator(FolderModel, name="FolderIn", exclude_readonly=True)


async def add_folder(folder: FolderIn, user) -> PydanticModel:
    async with in_transaction() as con:
        existing_folder = await FolderModel.filter(name=folder.name, create_by=user.id).first()
        if existing_folder:
            raise ValueError("该文件夹名已存在")
        d = folder.dict()
        d['create_by'] = user.id
        if 'id' in d:
            del d['id']
        folder_obj = await FolderModel.create(**d, using_db=con)
        r = await Folder_Pydantic.from_tortoise_orm(folder_obj)
        return r


async def delete_folder(folder_id: int):
    folder_obj = await FolderModel.get(id=folder_id)
    if not folder_obj:
        raise DoesNotExist("文件夹未找到")

    # 获取文件夹下的所有文件
    documents = await DocumentModel.filter(folder_id=folder_id)

    # 删除文件系统中的实际文件

    async with in_transaction() as con:
        # 根据文件Id删除掉该文件所在的所有知识库的记录
        rm = KnowledgeDocumentModel.filter(d_id__in=[doc.id for doc in documents]).using_db(con).delete()
        # 删除数据库中的文件记录
        rma = DocumentModel.filter(folder_id=folder_id).using_db(con).delete()
        # 删除文件夹记录
        rmb = FolderModel.filter(id=folder_id).using_db(con).delete()
        # 使用 asyncio.gather 并设置 return_exceptions=True 处理失败
        await asyncio.gather(rm, rma, rmb, return_exceptions=True)

        await io_util.remove_files([document.path for document in documents])


async def get_all_folders(query: QueryData, user) -> dict:
    folders = await FolderModel.filter(create_by=user.id).offset((query.offset - 1) * query.limit).limit(
        query.limit).values()
    total = await FolderModel.filter(create_by=user.id).count()
    for folder in folders:
        folder['created'] = folder['created'].strftime('%Y-%m-%d %H:%M:%S')
        folder['modified'] = folder['modified'].strftime('%Y-%m-%d %H:%M:%S')

    return {
        "total": total,
        "items": folders
    }


async def get_folder_by_id(folder_id: int) -> type[FolderOut, None]:
    try:
        folder_obj = await FolderModel.get(id=folder_id)
        if not folder_obj:
            return None
        return await Folder_Pydantic.from_tortoise_orm(folder_obj)
    except Exception as e:
        return None


async def get_all_folders_with_documents(user) -> List[FolderWithDocumentsOut]:
    query = BaseSchema.QueryData(offset=1, limit=999999)
    folders = await get_all_folders(query, user)
    folders_with_documents = []
    for folder in folders['items']:
        try:
            documents = await DocumentModel.filter(folder_id=folder['id'])
            documents_out = [await Document_Pydantic.from_tortoise_orm(doc) for doc in documents]
            logger.info(f"Documents for folder {folder['id']} found: {documents_out}")
        except Exception as e:
            logger.error(f"Error fetching documents for folder ID {folder['id']}: {e}")
            documents_out = []

        folder = FolderSimple(id=folder['id'], name=folder['name'])
        documents_basic = [DocumentBasic(
            id=doc.id,
            name=doc.name,
            path=doc.path,
            size=doc.size,
            mime_type=doc.mime_type
        ) for doc in documents_out]

        folder_with_documents = FolderWithDocumentsOut(
            folder=folder,
            documents=documents_basic
        )
        folders_with_documents.append(folder_with_documents)

    return folders_with_documents


async def split_setting(document_setting: SplitSetting):
    async with in_transaction() as conn:
        split_length = document_setting.split_length
        split_overlap = document_setting.split_overlap
        document_ids = document_setting.documentIds
        knowledge_id = document_setting.knowledgeId
        try:
            for document_id in document_ids:
                doc = await KnowledgeDocumentModel.get(d_id=document_id, k_id=knowledge_id).using_db(conn)
                doc.split_length = split_length
                doc.split_overlap = split_overlap
                await doc.save(using_db=conn)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"文档ID {document_ids} 不存在")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


async def get_document_settings(document_id, knowledge_id):
    async with in_transaction() as conn:
        try:
            doc = await KnowledgeDocumentModel.get(d_id=document_id, k_id=knowledge_id).using_db(conn)
            return {
                "split_length": doc.split_length,
                "split_overlap": doc.split_overlap,
                "data_classification": doc.classification,
                "open_theme_split": doc.open_theme_split,
                "assistant_id": doc.assistant_id
            }
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"文档ID {document_id} 不存在")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取文档设置失败: {str(e)}")


async def analysis_document(document_analysis: DocumentAnalysis, task: AnalysisTask):
    async with in_transaction() as conn:
        knowledge = await KnowledgeModel.filter(id=document_analysis.knowledge_id).using_db(conn).first()
        if not knowledge:
            raise HTTPException(status_code=404, detail=f"知识库ID {document_analysis.knowledge_id} 不存在")
        index_name = knowledge.index_name

        documentIds = document_analysis.documentIds
        knowledge_id = document_analysis.knowledge_id
        try:
            for document_id in documentIds:
                document = await KnowledgeDocumentModel.filter(d_id=document_id, k_id=knowledge_id).using_db(
                    conn).get_or_none()
                if not document:
                    raise HTTPException(status_code=404, detail="没有找到相关文档")

                document_info = await DocumentModel.get(id=document_id).using_db(conn)
                await task.add_vector_task(
                    [VectorTask(collection_name=index_name, file_path=document_info.path, file_name=document_info.name,
                                d_id=document_info.id, k_id=document_analysis.knowledge_id,
                                mimetype=document_info.mime_type,
                                split_length=document.split_length,
                                split_overlap=document.split_overlap
                                )]
                )

            await KnowledgeDocumentModel.filter(d_id__in=documentIds, k_id=knowledge_id).update(status_code=0,
                                                                                                status_text="排队中")
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="查询对象不存在")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文档分析出错: {str(e)}")


# 检测文件夹类是否存在
async def check_folder(folder):
    existing_folder = await FolderModel.filter(name=folder.name).first()
    print('数据类型', type(existing_folder))
    if existing_folder:
        return existing_folder
    return None
