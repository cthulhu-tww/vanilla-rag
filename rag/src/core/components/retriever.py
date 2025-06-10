import json
import re
from typing import List

from haystack import Document
from haystack.components.builders import PromptBuilder
from pymilvus import WeightedRanker, AnnSearchRequest, AsyncMilvusClient

from src.core.components.reranker import Reranker
from src.core.components.embedding import FlagEmbedding
from src.core.components.generator import Generator
from src.core.components.milvus_manager import MilvusManager
from src.core.entity.entity import Message, RetrieverConfig
from src.core.util.decorators import retry_on_error


class Retriever:
    def __init__(self, context: List[Message],
                 llm: Generator, model: str,
                 async_client: AsyncMilvusClient,
                 retriever_config: RetrieverConfig):
        self.sub_query_vectors = None
        self.keywords_vector = None
        self.llm = llm
        self.model = model
        if len(context) == 0:
            raise ValueError("context cannot be None")
        self.query = context[len(context) - 1].content
        self.context = context
        self.sub_query = [self.query]
        self.keywords = ''
        self.filenames = []
        self.async_client = async_client
        self.retriever_config = retriever_config
        self.ready = False
        self.embedder = FlagEmbedding()
        self.reranker = Reranker()

    async def warm_up(self):
        """重写用户查询"""
        await self._rewrite_query()
        self.keywords_vector = (await self.embedder.run([self.keywords]))[0]
        self.sub_query_vectors = (await self.embedder.run(self.sub_query))
        self.ready = True
        return self

    @retry_on_error(max_retries=5, delay=2)
    async def _rewrite_query(self):
        """
        重写query
        1.提取query中的关键信息，比如用户提供的文档名称等元数据。
        2.重写用户的问题，使之与上下文更加贴合。
        3.将用户的问题切分为子问题。
        """
        prompt = """
            请将用户问题拆解为适合BM25关键词匹配和向量语义检索的混合指令，要求：
            
            1. **BM25检索**：
               - 提取多个精确术语(含领域专有名词)
               - 扩展同义词
               - 可能会出现在答案中的关键字(假设单词嵌入)
            2. **向量检索**：
               - 生成多句语义完整子句
               - 排除停用词但保留逻辑关系词
               - 包含生成一个抽象的Step-Back查询，Step-Back 需要抽象，以及一阵见血。
            3. filenames: 用户在查询中提供的文件名称或者表名,数组类型，如果没有则为空.
            4. 你的思考不允许思考如何回答用户的问题，而是必须思考这个指令
            
            ### 输出格式
            ```json
            {
              "filenames":["实际文档名称。不允许有mimetype后缀"],
              "BM25_params": {
                "keywords": ["工业革命", "碳排放量","绝对值"],
                "synonym": ["机械革命","工业化浪潮","第一次/第二次工业革命","二氧化碳排放量","碳足迹","碳输出","无符号值","标量值"]
              },
              "vector_prompts": [
                "工业革命引发的碳排放对现代能源转型的影响",
                "气候变化应对措施与历史排放的关联性分析"
              ]
            }
            用户问题: {{question}}
            用户对话上下文:
            {% for c in context %}
                {{c.role}}:{{c.content}}
            {% endfor %}
        """
        prompt_builder = PromptBuilder(template=prompt)
        builder_result = prompt_builder.run(template_variables={"context": self.context, "question": self.query})
        response = await self.llm.generate(
            messages=[{
                "role": "user",
                "content": builder_result['prompt']
            }], model=self.model
        )
        json_str = re.search(r'```json\n(.*?)\n```', response['message']['content'], re.DOTALL).group(1)
        r = json.loads(json_str)

        self.sub_query = r['vector_prompts'] if len(r['vector_prompts']) > 0 else [self.query]
        keywords = ""
        if len(r['BM25_params']['keywords']) > 0:
            keywords = ','.join(r['BM25_params']['keywords'])

        if len(r['BM25_params']['synonym']) > 0:
            keywords += ',' + ','.join(r['BM25_params']['synonym'])

        self.keywords = keywords if len(keywords) > 0 else self.query

        if 'filenames' in r:
            self.filenames = r['filenames']

    @retry_on_error(max_retries=5, delay=2)
    async def vector_retrieval(self, collection_name: str):
        """向量检索"""
        if self.ready is False:
            raise ValueError("请先调用warm_up方法")

        result = []
        for sub_query_vector in self.sub_query_vectors:
            datas = [
                {
                    "field_name": "vector",
                    "vector": [sub_query_vector['dense']],
                    "param": {
                        "metric_type": "COSINE",
                    },
                    "weight": 1 - self.retriever_config.keyword_weight,
                },
                {
                    "field_name": "sparse_vector",
                    "vector": [self.keywords_vector['sparse']],
                    "param": {
                        "metric_type": "IP",
                    },
                    "weight": self.retriever_config.keyword_weight
                }
            ]

            _filter = ""
            for filename in self.filenames:
                _filter += f"TEXT_MATCH(file_name, '{filename}') OR "

            if _filter != "":
                _filter = _filter[:-4]

            r = await self._hybrid_retrieval_from_milvus(datas=datas, _filter=_filter,
                                                         collection_name=collection_name)
            docs = self._milvus_obj_to_doc(r)
            docs = await self.reranker.run(sub_query_vector['text'], docs, self.retriever_config.rerank_top_k,
                                           self.retriever_config.rerank_similarity_threshold)
            docs = self._reorder(docs)
            result.extend(docs)

        # 根据文档id 去重
        result = list({d.id: d for d in result}.values())
        # 找出所有excel表格 以source_id 去重代表同一个表格
        try:
            tables = list({d.meta['source_id']: d for d in [r for r in result if
                                                            (r.meta['file_name'].endswith('.xlsx') or
                                                             r.meta[
                                                                 'file_name'].endswith('.xls')
                                                             )]}.values())
            if len(tables) > 0:
                for doc in tables:
                    content = ""
                    r = self._reorder(await self._windows_retrieval(doc, collection_name))
                    for r in r:
                        content += r.content
                    doc.content = content
                return tables
        except Exception as e:
            print(e)
        return result

    async def _windows_retrieval(self, doc: Document, collection_name: str, length: int = -1):
        """窗口检索
        length: -1 ~ 正无穷整数
        """
        if self.ready is False:
            raise ValueError("请先调用warm_up方法")

        split_id = doc.meta['split_id']
        source_id = doc.meta['source_id']
        if length == -1:
            r = await self.filter(f"(split_id >= 0 or split_id >={split_id}) and source_id == '{source_id}'",
                                  collection_name=collection_name)
            return r

        r = await self.filter(
            f"(split_id >= {split_id - length} and split_id <={split_id + length})  and source_id == '{source_id}'",
            collection_name=collection_name)
        return r

    def _reorder(self, docs: []):
        """将docs 按照文档的chunk顺序排列"""
        group = {}
        for d in docs:
            key = d.meta['source_id']
            if key not in group:
                group[key] = []
            group[key].append(d)

        result = []
        for d in group.values():
            d.sort(key=lambda x: x.meta['split_id'])
            result.extend(d)

        return result

    def _milvus_obj_to_doc(self, r):
        # todo vector 中的 字段属性 需要处理 vector中是 text 而 Document 对象要求是content，可能要将整个haystack 框架替替换成自实现
        return [Document.from_dict({
            'id': i['id'],
            'content': i['entity']['text'] if 'text' in i['entity'] else i['entity']['content'],
            'score': i['distance'],
            **i['entity']
        }) for i in r[0]]

    async def filter(self, _filter: str, collection_name: str) -> list[Document]:
        fields_names = [field.name for field in MilvusManager.get_field_schema()[0]]
        r = await self.async_client.query(collection_name=collection_name, filter=_filter, output_fields=fields_names)
        return [Document.from_dict({
            'id': i['id'],
            'content': i['text'] if 'text' in i else i['content'],
            **i
        }) for i in r]

    async def _hybrid_retrieval_from_milvus(self, datas: [dict], _filter: str, collection_name):
        """
        从milvus中检索
        data : {
        "field_name":向量字段名
        "vector": [稀疏/密集向量]
        "param":dict 检索参数
        weight:float 权重
        }

        filter: 过滤条件，详细见milvus文档

        """
        reqs = []
        weights = []
        for data in datas:
            p = {
                "data": data['vector'],
                "anns_field": data["field_name"],
                "param": data['param'],
                "limit": self.retriever_config.retriever_top_k
            }
            reqs.append(AnnSearchRequest(**p))
            weights.append(data['weight'])

        reranker = WeightedRanker(*weights)
        fields_names = [field.name for field in MilvusManager.get_field_schema()[0]]
        r = await self.async_client.hybrid_search(
            collection_name=collection_name,
            reqs=reqs,
            output_fields=fields_names,
            ranker=reranker,
            filter=_filter,
            limit=self.retriever_config.retriever_top_k
        )
        return r
