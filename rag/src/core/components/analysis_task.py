import asyncio

from tortoise import Tortoise

from src.core.components.embedding import FlagEmbedding
from src.core.components.milvus_manager import MilvusManager
from src.core.components.spliter import Spliter
from src.core.util import io_util
from src.server.entity import KnowledgeModel, KnowledgeDocumentModel


class VectorTask:
    collection_name = ""
    split_length = 20
    split_overlap = 4
    file_path = ""
    mimetype = ""
    file_name = ""
    d_id = 0
    k_id = 0
    status_code = 0
    status_text = ""
    source_id = ""

    def __init__(self, collection_name: str, file_path: str, file_name: str, d_id: int, k_id: int, mimetype: str,
                 status_code: int = 0,
                 status_text: str = "",
                 source_id: str = "",
                 split_length: int = 20,
                 split_overlap: int = 4
                 ):
        self.collection_name = collection_name
        self.file_path = file_path
        self.file_name = file_name
        self.d_id = d_id
        self.k_id = k_id
        self.mimetype = mimetype
        self.status_code = status_code
        self.status_text = status_text
        self.source_id = source_id
        self.split_length = split_length
        self.split_overlap = split_overlap


class AnalysisTask:
    """
    用于管理解析任务的类
    """

    def __init__(self, milvus_manager: MilvusManager):
        if milvus_manager is None:
            raise ValueError("milvus_manager cannot be None")
        self.milvus_manager = milvus_manager
        self.vector_task_queue = asyncio.Queue()

    async def add_vector_task(self, vector_tasks: [VectorTask]):
        for vector_task in vector_tasks:
            self.vector_task_queue.put_nowait(vector_task)

    async def analysis(self, vector_task: VectorTask):
        file_path = vector_task.file_path
        d_id = vector_task.d_id
        k_id = vector_task.k_id
        file_name = vector_task.file_name
        collection_name = vector_task.collection_name

        try:
            # 查询数据库，如果查不到这个知识库中的这个文档，就代表已经被删除，就不再执行解析任务
            knowledge_doc = await KnowledgeDocumentModel.filter(k_id=k_id, d_id=d_id).get_or_none()
            if knowledge_doc is None:
                return

            await KnowledgeDocumentModel.filter(k_id=k_id, d_id=d_id).update(
                status_text=f"解析中", status_code=1)

            spliter = Spliter(collection_name=collection_name)
            docs = await spliter.run(data=await io_util.get_file(file_path),
                                     mime_type=vector_task.mimetype,
                                     file_name=file_name,
                                     split_length=vector_task.split_length,
                                     split_overlap=vector_task.split_overlap)
            # 在执行嵌入模型前再次检查文档是否存在
            knowledge_doc = await KnowledgeDocumentModel.filter(k_id=k_id, d_id=d_id).get_or_none()
            if knowledge_doc is None:
                return

            # 通过 k_id 查询知识库类型
            knowledge_base = await KnowledgeModel.filter(id=k_id).get_or_none()
            if knowledge_base is None:
                return

            print("************** start embedding documents **************")
            embedder = FlagEmbedding()
            r = await embedder.embedding_documents(docs)
            count = await self.milvus_manager.insert_data(collection_name=collection_name,
                                                          data=r)

            print(f"文档数量: {count['insert_count']}")

            await KnowledgeDocumentModel.filter(k_id=k_id, d_id=d_id).update(
                status_text=f"解析成功", status_code=3, source_id=docs[0].meta['source_id'])

        except Exception as e:
            print(f"解析任务出错: {e}")
            await KnowledgeDocumentModel.filter(k_id=k_id, d_id=d_id).update(
                status_text=f"服务器错误", status_code=2)

    async def get_processing_task_status(self):
        """`
        獲取所有非解析完成狀態的doc
        """
        sql = """
        SELECT 
        skd.*,
        sd.`path` as file_path,
        sk.index_name as collection_name,
        sd.`mime_type` as mime_type,
        sd.name as file_name
        from sys_knowledge_document skd  
        join sys_document sd on skd.d_id = sd.id 
        join sys_knowledge sk on skd.k_id = sk.id 
        where skd.status_code not in (3,4)
        """
        docs = await Tortoise.get_connection("default").execute_query_dict(sql)
        result = [VectorTask(
            collection_name=d['collection_name'],
            file_name=d['file_name'],
            file_path=d['file_path'],
            k_id=d['k_id'],
            d_id=d['d_id'],
            mimetype=d['mime_type'],
            status_code=d['status_code'],
            status_text=d['status_text'],
            source_id=d['source_id'],
        ) for d in docs]
        return result

    async def run(self):
        print("开启解析任务------------->>>>>>>>>>>>>>>>>>")
        tasks = await self.get_processing_task_status()
        for t in tasks:
            await self.add_vector_task([t])
        while True:
            # 从队列中取出一条任务（阻塞直到有任务可用）
            vector_task = await self.vector_task_queue.get()
            if vector_task is None:
                continue

            try:
                print(f"Executing task: {vector_task}")
                await asyncio.sleep(5)
                await self.analysis(vector_task)
            except Exception as e:
                print(e)
                print(f"解析失败----->{vector_task.file_name}")
            finally:
                self.vector_task_queue.task_done()  # 标记任务已完成
