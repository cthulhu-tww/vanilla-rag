from concurrent.futures import ThreadPoolExecutor

from src.core.components.embedding import FlagEmbedding
from src.core.components.reranker import Reranker

rerank_model = Reranker()
text_embedder = FlagEmbedding()
# 创建一个全局的线程池
executor = ThreadPoolExecutor()
