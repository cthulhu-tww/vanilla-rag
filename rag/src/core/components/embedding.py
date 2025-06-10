from copy import deepcopy
from typing import List

import aiohttp
from haystack import Document

from src.core.config import config


class FlagEmbedding:

    async def embedding_documents(self, documents: List[Document]) -> list[dict]:
        _docs = []
        for d in deepcopy(documents):
            d = d.__dict__
            if 'meta' in d:
                for key, value in d['meta'].items():
                    d[key] = value
                del d['meta']
            _docs.append(d)
        r = await self.embedding([d['content'] for d in _docs])
        for d, j in zip(_docs, r):
            d['vector'] = j['dense']
            d['sparse_vector'] = j['sparse']
        return _docs

    async def run(self, text: list[str]):
        return await self.embedding(text)

    async def embedding(self, texts: list[str]):
        host = config.interface["inference"]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{host}/embedding",
                                        timeout=-1,
                                        json=texts,
                                        headers={"Content-Type": "application/json"},
                                        ) as response:
                    response.raise_for_status()  # 检查 HTTP 错误
                    data = await response.json()
                    return data
            except aiohttp.ClientError as e:
                return {"error": f"HTTP error occurred: {str(e)}"}
            except Exception as e:
                return {"error": f"An error occurred: {str(e)}"}
