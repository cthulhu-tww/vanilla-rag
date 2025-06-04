# -*- coding: utf-8 -*-
from src.core.components.document_store import MilvusDocumentStore
from src.core.config import config
from src.server.entity import KnowledgeModel

document_stores = {}


def get_collection(index_name):
    try:
        s = document_stores[index_name]
    except Exception as e:
        raise ValueError("知识库异常，请确认知识库是否存在")
    return s


async def get_reality_collection():
    knowledges = await KnowledgeModel.all().order_by('-created')
    return knowledges


# 创建所有表的链接
async def init_stores():
    global document_stores
    db_knowledges = await get_reality_collection()
    collection_names = [col.index_name for col in db_knowledges]
    for name in collection_names:
        document_stores[name] = MilvusDocumentStore(
            collection_name=name,
            index_params={
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64},
            },
            connection_args={
                "host": config.milvus["host"],
                "port": config.milvus["port"],
                "user": config.milvus["user"],
                "password": config.milvus["password"],
                "secure": False,
            },
            sparse_vector_field="sparse_vector",  # 开启sparse检索支持
            drop_old=False,
            enable_text_match=True
        )
