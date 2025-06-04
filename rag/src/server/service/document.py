from typing import List

from fastapi import UploadFile, Request
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic, in_transaction

from src.server.entity import DocumentModel, KnowledgeDocumentModel
from src.server.schemas.common import QueryData, ListAll
from src.server.schemas.document import DocumentOut, KnowledgeDocumentOut, DocumentClassification
from src.core.util import io_util
from src.server.entity import KnowledgeModel

# 创建 Pydantic 模型转换器
Document_Pydantic = pydantic_model_creator(DocumentModel, name="Document")
DocumentIn_Pydantic = pydantic_model_creator(DocumentModel, name="DocumentIn", exclude_readonly=True)
KnowledgeDocument_Pydantic = pydantic_model_creator(KnowledgeDocumentModel, name="KnowledgeDocument")


@atomic()
async def upload_document(file: UploadFile, folder_id: int) -> DocumentOut:
    # 检查同一文件夹下是否有相同名称的文件
    existing_document = await DocumentModel.filter(name=file.filename, folder_id=folder_id).first()
    if existing_document:
        raise ValueError("该文件夹下已存在相同名称的文件")

    # 上传minio
    path = await io_util.upload(data=await file.read(), filename=file.filename)

    document_data = {
        "name": file.filename,
        "path": path,
        "size": file.size // 1024,
        "mime_type": file.content_type,
        "folder_id": folder_id,
    }

    document_obj = await DocumentModel.create(**document_data)
    return await Document_Pydantic.from_tortoise_orm(document_obj)


async def get_all_documents(folder_id: int, query: QueryData) -> ListAll[DocumentOut]:
    total = await DocumentModel.filter(folder_id=folder_id).count()
    document_objs = await DocumentModel.filter(folder_id=folder_id).offset((query.offset - 1) * query.limit).limit(
        query.limit)
    document_data_list = []
    for document_obj in document_objs:
        document_data = await Document_Pydantic.from_tortoise_orm(document_obj)
        document_out = DocumentOut(**document_data.dict())
        document_data_list.append(document_out)
    return ListAll(total=total, items=document_data_list)


async def delete_document(document_id: int):
    document_obj = await DocumentModel.get(id=document_id)
    if not document_obj:
        raise DoesNotExist("文档未找到")

    # 根据文件Id删除掉该文件所在的所有知识库的记录
    await KnowledgeDocumentModel.filter(d_id=document_id).delete()

    await document_obj.delete()
    await io_util.remove_files([document_obj.path])


async def get_documents_by_knowledge(knowledge_id: int, offset, limit) -> ListAll[KnowledgeDocumentOut]:
    knowledge_documents = await KnowledgeDocumentModel.filter(k_id=knowledge_id).offset((offset - 1) * limit).limit(
        limit).values()
    total = await KnowledgeDocumentModel.filter(k_id=knowledge_id).count()
    if not knowledge_documents:
        return ListAll(total=0, items=[])

    d_ids = [kd['d_id'] for kd in knowledge_documents]
    knowledge_dict = {kd['d_id']: kd for kd in knowledge_documents}

    documents = []

    db_docs = await DocumentModel.filter(id__in=d_ids).all()

    for db_doc in db_docs:
        knowledge_document = knowledge_dict.get(db_doc.id)
        if knowledge_document is not None:
            code = knowledge_document['status_code']
            text = knowledge_document['status_text']
            document = await Document_Pydantic.from_tortoise_orm(db_doc)
            document_with_status = KnowledgeDocumentOut(
                **document.model_dump(),
                status_code=code,
                status_text=text,
                split_length=knowledge_document['split_length'],
                split_overlap=knowledge_document['split_overlap'],
            )
            documents.append(document_with_status)

    return ListAll(total=total, items=documents)


async def save_documents_to_knowledge(knowledge_id: int, document_ids: List[int]):
    for item in await KnowledgeDocumentModel.filter(k_id=knowledge_id, d_id__in=document_ids):
        document_ids.remove(item.d_id)

    return await KnowledgeDocumentModel.bulk_create(
        [KnowledgeDocumentModel(k_id=knowledge_id, d_id=d_id, split_length=5, split_overlap=0, status_text="未解析",
                                status_code=4) for d_id in
         document_ids])


# 获取文档内容
async def get_documents(document_id: int):
    try:
        document = await DocumentModel.get(id=document_id)
        return await Document_Pydantic.from_tortoise_orm(document)
    except Exception as e:
        print(e)
        return None


async def update_document_classification(data: DocumentClassification):
    async with in_transaction() as conn:
        document_ids = data.d_ids
        knowledge_id = data.k_id
        classification = data.classification
        for document_id in document_ids:
            documents = await KnowledgeDocumentModel.filter(d_id=document_id, k_id=knowledge_id).using_db(conn)
            if not documents:
                raise DoesNotExist("文档不存在")
            for doc in documents:
                doc.classification = classification
                await doc.save(using_db=conn)


async def delete_documents_by_knowledge(knowledge_id, document_ids, request: Request):
    milvus_client = request.app.state.async_milvus_client
    knowledge = await KnowledgeModel.filter(id=knowledge_id).get()
    collection_name = knowledge.index_name

    # 获取知识库文档
    knowledge_documents = await KnowledgeDocumentModel.filter(k_id=knowledge_id, d_id__in=document_ids).all()
    source_ids = [d.source_id for d in knowledge_documents]

    # 删除知识库文档
    await KnowledgeDocumentModel.filter(k_id=knowledge_id, d_id__in=document_ids).delete()

    if len(source_ids) > 0:
        try:
            await milvus_client.delete(collection_name=collection_name, filter=f"""
                   source_id in {source_ids}
                   """)
        except Exception as e:
            print(e)
            pass
    return None
