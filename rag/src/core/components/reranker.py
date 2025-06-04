import aiohttp
from haystack import Document

from src.core.config import config


class Reranker:

    async def run(self, query: str, documents: list[Document], top_n: int = 10, top_c: float = 0.1):
        if len(documents) == 0:
            return []
        compare = [[query, f"{doc.meta['file_name']} \n {doc.content}" if 'file_name' in doc.meta else f"{doc.content}"]
                   for doc in documents]

        scores = await self.rerank(compare)
        for index, score in enumerate(scores):
            documents[index].rerank_score = score
        origin_sorted = sorted(documents, key=lambda doc: doc.rerank_score, reverse=True)
        f = filter(lambda doc: doc.rerank_score > top_c, origin_sorted)
        return list(f)[:top_n]

    async def rerank(self, compare: [[str, str]]):
        host = config.interface["inference"]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{host}/rerank",
                                        timeout=-1,
                                        json=compare,
                                        headers={"Content-Type": "application/json"},
                                        ) as response:
                    response.raise_for_status()  # 检查 HTTP 错误
                    data = await response.json()
                    return data
            except aiohttp.ClientError as e:
                return {"error": f"HTTP error occurred: {str(e)}"}
            except Exception as e:
                return {"error": f"An error occurred: {str(e)}"}
