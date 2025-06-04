from typing import Optional, List

import aiohttp
from haystack import Document
from haystack.dataclasses import SparseEmbedding

from src.core.config import config


class FlagEmbedding:

    def __init__(
            self,
            meta_fields_to_embed: Optional[List[str]] = None,
            embedding_separator: str = "\n",
    ):

        self.meta_fields_to_embed = meta_fields_to_embed or []
        self.embedding_separator = embedding_separator

    async def run_documents(self, documents: List[Document]):
        """
        Embed a list of Documents.

        :param documents:
            Documents to embed.

        :returns:
            A dictionary with the following keys:
            - `documents`: Documents with embeddings
        """
        if not isinstance(documents, list) or documents and not isinstance(documents[0], Document):
            raise TypeError(
                "EmbedderDocument expects a list of Documents as input."
                "In case you want to embed a list of strings, please use the Embedding."
            )

        texts_to_embed = []
        for doc in documents:
            meta_values_to_embed = [
                str(doc.meta[key]) for key in self.meta_fields_to_embed if key in doc.meta and doc.meta[key]
            ]
            text_to_embed = (
                self.embedding_separator.join(meta_values_to_embed + [doc.content] or "")
            )
            texts_to_embed.append(text_to_embed)

        r = await self.embedding(texts_to_embed)
        for d, j in zip(documents, r):
            d.embedding = j['dense']
            d.sparse_embedding = SparseEmbedding(indices=list(j['sparse'].keys()), values=list(j['sparse'].values()))

        return {"documents": documents}

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
