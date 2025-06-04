import asyncio
from datetime import datetime

from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from src.server.entity import KnowledgeModel, KnowledgeDocumentModel
from src.server.schemas.common import QueryData
from src.server.schemas.knowledge import KnowledgeIn, KnowledgeOut

# 创建 Pydantic 模型转换器
KnowledgeIn_Pydantic = pydantic_model_creator(KnowledgeModel, name="KnowledgeIn", exclude_readonly=True)


async def addKnowledge(knowledge: KnowledgeIn, user) -> KnowledgeOut:
    # 检查是否存在相同名称的知识库
    async with in_transaction() as con:
        existing_knowledge = await KnowledgeModel.filter(name=knowledge.name, create_by=user.id).first()
        if existing_knowledge:
            raise ValueError("该知识库名已存在")
        create_data = knowledge.model_dump(exclude={'id'})  # 不传 id
        create_data['create_by'] = user.id
        knowledge_obj = await KnowledgeModel.create(**create_data, using_db=con)
        # 转换为输出模型返回
        return KnowledgeOut(
            **knowledge_obj.__dict__,
            document_count=0  # 假设初始文档数为 0
        )


async def getAllKnowledge(query: QueryData, user) -> dict:
    total = await KnowledgeModel.filter(create_by=user.id).count()
    knowledge_objs = await KnowledgeModel.filter(create_by=user.id).offset((query.offset - 1) * query.limit).limit(
        query.limit).values()

    items = []
    for knowledge in knowledge_objs:
        doc_count = await KnowledgeDocumentModel.filter(k_id=knowledge['id']).count()

        # 格式化时间为字符串
        created_str = knowledge['created'].strftime("%Y-%m-%d %H:%M:%S")
        modified_str = knowledge['modified'].strftime("%Y-%m-%d %H:%M:%S")

        # 构造 KnowledgeOut 对象
        items.append({
            "id": knowledge['id'],
            "label": knowledge['label'],
            "name": knowledge['name'],
            "description": knowledge['description'],
            "created": created_str,
            "modified": modified_str,
            "document_count": doc_count,
            "index_name": knowledge['index_name']
        })
    return {
        "total": total,
        "items": items
    }


async def getKnowledge(knowledge_id: int) -> KnowledgeOut:
    knowledge_obj = await KnowledgeModel.get(id=knowledge_id)
    document_count = await KnowledgeDocumentModel.filter(k_id=knowledge_id).count()
    return KnowledgeOut(**knowledge_obj.__dict__, document_count=document_count)


async def updateKnowledge(knowledge_id: int, knowledge_in: KnowledgeIn) -> KnowledgeOut:
    try:
        # 获取待更新的知识库对象
        knowledge_db = await KnowledgeModel.get(id=knowledge_id)
    except DoesNotExist:
        raise DoesNotExist("知识库未找到")

    # 校验 name 是否为空
    if not knowledge_in.name or knowledge_in.name.strip() == "":
        raise ValueError("知识库名称不能为空")

    # 判断 name 是否被修改
    if knowledge_in.name != knowledge_db.name:
        # 构建查询条件
        query = KnowledgeModel.filter(name=knowledge_in.name)

        # 获取当前知识库的创建人 ID
        current_creator_id = knowledge_db.create_by

        # 如果是有用户的知识库，则限制为该用户
        if current_creator_id != 0:
            query = query.filter(create_by=current_creator_id)
        else:
            query = query.filter(create_by=0)

        # 排除自己
        query = query.exclude(id=knowledge_id)

        # 检查是否已存在
        if await query.exists():
            if current_creator_id != 0:
                raise ValueError("该用户下已存在同名的知识库")
            else:
                raise ValueError("知识库名称已存在")

    # 更新字段
    knowledge_db.label = knowledge_in.label
    knowledge_db.name = knowledge_in.name
    knowledge_db.description = knowledge_in.description

    # 保存更新
    await knowledge_db.save()

    # 获取文档数量（假设文档表中有一个外键指向知识库）
    document_count = await KnowledgeDocumentModel.filter(k_id=knowledge_id).count()

    # 构造返回对象
    return KnowledgeOut(
        id=knowledge_db.id,
        label=knowledge_db.label,
        name=knowledge_db.name,
        description=knowledge_db.description,
        created=knowledge_db.created,
        modified=knowledge_db.modified,
        document_count=document_count
    )


async def deleteKnowledge(knowledge_id: int):
    async with in_transaction() as connection:
        # 获取知识库
        knowledge = await KnowledgeModel.get_or_none(id=knowledge_id)
        if knowledge is None:
            raise DoesNotExist("知识库未找到")

        # 删除知识库文档中间表中的关联信息
        await asyncio.gather(
            KnowledgeDocumentModel.filter(k_id=knowledge_id).using_db(connection).delete(),
            # 删除知识库本身
            KnowledgeModel.filter(id=knowledge_id).using_db(connection).delete(),
        )


async def get_documents_by_sourceIds(sourceIds: list[str]) -> list[dict]:
    if not sourceIds:
        return []

    placeholder = ", ".join(["?"] * len(sourceIds))

    sql = f"""
    SELECT sk.name, sd.created, skd.source_id  
    FROM sys_knowledge_document skd 
    JOIN sys_document sd ON skd.d_id = sd.id
    JOIN sys_knowledge sk ON skd.k_id = sk.id 
    WHERE skd.source_id IN ({placeholder})
    """

    (count, results) = await Tortoise.get_connection("default").execute_query(sql, sourceIds)

    return [
        {
            "source_name": r['name'],
            "create_time": datetime.fromisoformat(r['created']),  # 自动识别 ISO 格式
            "source_id": r['source_id']
        }
        for r in results
    ]
