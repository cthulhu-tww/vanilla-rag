import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any

import aiohttp
from haystack import component, Document
from haystack.components.converters.utils import normalize_metadata
from haystack.dataclasses import ByteStream

from src.core.config import config

logger = logging.getLogger(__name__)


@component
class PdfToDocument:

    @component.output_types(documents=List[Document])
    def run(
            self,
            sources: List[Union[str, Path, ByteStream]],
            meta: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        pass

    @component.output_types(documents=List[Document])
    async def run_async(
            self,
            sources: List[Union[str, Path, ByteStream]],
            meta: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        documents = []
        meta_list = normalize_metadata(meta, sources_count=len(sources))
        for source, metadata in zip(sources, meta_list):
            json = await self.convert_pdf(source.data, source.meta['file_name'], source.mime_type)
            text = json['text']
            document = Document(content=text, meta={"file_path": ""})
            documents.append(document)
        return {"documents": documents}

    async def convert_pdf(self, file_bytes: list[bytes], file_name, content_type) -> dict:
        host = config.interface["inference"]
        data = aiohttp.FormData()
        data.add_field(
            "file",
            file_bytes,
            filename=file_name,
            content_type=content_type
        )
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{host}/ocr",
                                        timeout=None,
                                        data=data,
                                        ) as response:
                    response.raise_for_status()  # 检查 HTTP 错误
                    data = await response.json()
                    return data
            except aiohttp.ClientError as e:
                return {"error": f"HTTP error occurred: {str(e)}"}
            except Exception as e:
                return {"error": f"An error occurred: {str(e)}"}
