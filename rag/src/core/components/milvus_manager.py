import logging

from pymilvus import AsyncMilvusClient, CollectionSchema, FieldSchema, MilvusException, DataType
from pymilvus.milvus_client import IndexParams

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MilvusManager:
    collections = []

    def __init__(self, client: AsyncMilvusClient):
        if client is None:
            raise ValueError("milvus 客户端不能为空")
        self.client = client

    async def load_collections(self, collection_names: list):
        for name in collection_names:
            try:
                await self.client.load_collection(name)
                if name not in self.collections:
                    self.collections.append(name)
            except MilvusException as e:
                logger.error(f"初始化collection失败，name:{name},error info:{e}")
                pass

    async def create_collection(self, name: str, dim: int = 1024):
        fields, index = self.get_field_schema(dim)
        try:
            schema = CollectionSchema(fields=fields)
            await self.client.create_collection(schema=schema, collection_name=name,
                                                index_params=index, primary_field_name="_id")
            await self.load_collections([name])
        except MilvusException as e:
            logger.error(f"创建collection失败，name:{name},error info:{e}")
            raise ValueError(f"创建collection失败，name:{name},error info:{e}")

    async def drop_collection(self, name: str):
        try:
            await self.client.drop_collection(name)
            if name in self.collections:
                self.collections.remove(name)
        except MilvusException as e:
            logger.error(f"删除collection失败，name:{name},error info:{e}")
            raise ValueError(f"删除collection失败，name:{name},error info:{e}")

    async def insert_data(self, collection_name: str, data: list[dict]):
        if collection_name is None:
            raise ValueError("collection_name不能为空")

        if collection_name not in self.collections:
            raise ValueError("milvus collection 不存在")

        names = [k.name for k in self.get_field_schema()[0]]
        r = await self.client.insert(collection_name=collection_name,
                                     data=[{key: value for key, value in d.items() if (key in names and key != '_id')}
                                           for d
                                           in data])
        return r

    @staticmethod
    def get_field_schema(dim: int = 1024):
        index = IndexParams()
        fields = [
            FieldSchema(name='_id', dtype=DataType.INT64, description="自增id", is_primary=True, auto_id=True),
            FieldSchema(name='content', dtype=DataType.VARCHAR, description="内容字符串", max_length=65535),
            FieldSchema(name='source_id', dtype=DataType.VARCHAR, description="与文档绑定的唯一id", max_length=65535),
            FieldSchema(name='file_name', dtype=DataType.VARCHAR, description="文件名", max_length=65535),
            FieldSchema(name='page_number', dtype=DataType.INT64, description="分割用参数"),
            FieldSchema(name='split_id', dtype=DataType.INT64, description="分割用参数"),
            FieldSchema(name='split_idx_start', dtype=DataType.INT64, description="分割用参数"),
            FieldSchema(name='vector', dtype=DataType.FLOAT_VECTOR, description="密集向量", dim=dim),
            FieldSchema(name='sparse_vector', dtype=DataType.SPARSE_FLOAT_VECTOR, description="稀疏向量"),
        ]

        index.add_index(field_name="vector", index_type="HNSW",
                        M=8,
                        efConstruction=128,
                        metric_type='COSINE')
        index.add_index(field_name="sparse_vector",
                        index_type="SPARSE_INVERTED_INDEX",
                        metric_type='IP')
        return fields, index
