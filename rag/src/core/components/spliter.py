from io import BytesIO

from haystack import AsyncPipeline
from haystack.components.converters import TextFileToDocument, MarkdownToDocument, CSVToDocument
from haystack.components.joiners import DocumentJoiner
from haystack.components.routers import FileTypeRouter
from haystack.dataclasses import ByteStream
from pymilvus import AsyncMilvusClient
from src.core.components.multimodal2document import Multimodal2Document

from src.core.config import config
from src.core import text_embedder, rerank_model as rerank
from src.core.components.rag_spliter import RAGSplitter
from src.core.components.xlsx import XLSXToDocumentUpgrade


class Spliter:
    def __init__(self,
                 collection_name: str = None) -> None:

        if collection_name is None:
            raise ValueError("向量库索引名称必须指定。")

        self.collection_name = collection_name
        # 创建主题索引向量库
        self.client = AsyncMilvusClient(
            uri=f"http://{config.milvus['host']}:{config.milvus['port']}",
            user="root",
        )
        self.text_embedder = text_embedder
        self.rerank = rerank
        self.source_id = ""

    async def run(self, data: bytes,
                  file_name: str = "",
                  mime_type: str = "",
                  split_length=20,
                  split_overlap=4):
        is_excel = False
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            is_excel = True

        l = file_name.split(".")
        if len(l) <= 1:
            raise ValueError("文件名不正确。")
        byte_stream = ByteStream(data=BytesIO(data).getvalue(), mime_type=mime_type,
                                 meta={"file_name": file_name})

        self.file_name = file_name

        self.spliter = self.init_split_pipe(split_length=split_length,
                                            split_overlap=0 if is_excel else split_overlap,
                                            file_name=file_name)
        r = await self.spliter.run_async({"file_type_router": {
            "sources": [byte_stream]}})
        docs = r['splitter']['documents']
        if is_excel:
            # 如果是excel 将filename 换成 sheet_name
            for doc in docs:
                if 'xlsx' in doc.meta:
                    if 'sheet_name' in doc.meta['xlsx']:
                        doc.meta['file_name'] = doc.meta['xlsx']['sheet_name'] + ".xlsx"
                if 'xls' in doc.meta:
                    if 'sheet_name' in doc.meta['xls']:
                        doc.meta['file_name'] = doc.meta['xls']['sheet_name'] + ".xls"
        self.source_id = docs[0].meta['source_id']
        return docs

    async def embedding(self, themes: [dict]):
        themes_title, themes_content, themes_all_text = zip(*[
            (n['theme'], n['content'], f"{n['theme']}:{n['content']}") for n in themes
        ])
        """embedding 返回稀疏和密集向量"""
        theme_vector = [r['dense'] for r in (await self.text_embedder.run(themes_title))]
        content_vector = [r['dense'] for r in (await self.text_embedder.run(themes_content))]
        sparse_vector = [r['sparse'] for r in (await self.text_embedder.run(themes_all_text))]

        for i in range(len(themes)):
            themes[i]['theme_vector'] = theme_vector[i]
            themes[i]['content_vector'] = content_vector[i]
            themes[i]['sparse_vector'] = sparse_vector[i]

        return themes

    def init_split_pipe(self, split_length, split_overlap, file_name):
        """
        初始化常规spliter
        """
        pipe = AsyncPipeline()
        pipe.add_component(
            instance=FileTypeRouter(mime_types=["text/plain",
                                                "application/pdf",
                                                "text/markdown",
                                                "application/vnd.ms-powerpoint",
                                                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                "application/msword",
                                                "application/vnd.ms-excel",
                                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                "text/csv",
                                                "image/png",
                                                "image/jpeg",
                                                ]), name="file_type_router")

        pipe.add_component("text_converter", TextFileToDocument())
        pipe.add_component("pdf_converter", Multimodal2Document())
        pipe.add_component("png_converter", Multimodal2Document())
        pipe.add_component("jpg_converter", Multimodal2Document())
        pipe.add_component("markdown_converter", MarkdownToDocument())
        pipe.add_component("ppt_converter", Multimodal2Document())
        pipe.add_component("pptx_converter", Multimodal2Document())
        pipe.add_component("doc_converter", Multimodal2Document())
        pipe.add_component("docx_converter", Multimodal2Document())
        pipe.add_component("xls_converter", XLSXToDocumentUpgrade(table_format="markdown"))
        pipe.add_component("xlsx_converter", XLSXToDocumentUpgrade(table_format="markdown"))
        pipe.add_component("csv_converter", CSVToDocument())
        pipe.add_component("doc_joiner", DocumentJoiner())

        if split_overlap >= split_length:
            split_overlap = split_length - 1

        pipe.add_component("splitter",
                           RAGSplitter(split_by="sentence", split_length=split_length, split_overlap=split_overlap,
                                       split_threshold=round(split_length / 2),
                                       file_name=file_name))

        pipe.connect("file_type_router.text/plain", "text_converter.sources")
        pipe.connect("file_type_router.application/pdf", "pdf_converter.sources")
        pipe.connect("file_type_router.image/png", "png_converter.sources")
        pipe.connect("file_type_router.image/jpeg", "jpg_converter.sources")
        pipe.connect("file_type_router.text/markdown", "markdown_converter.sources")
        pipe.connect("file_type_router.application/vnd.ms-powerpoint", "ppt_converter.sources")
        pipe.connect("file_type_router.application/vnd.openxmlformats-officedocument.presentationml.presentation",
                     "pptx_converter.sources")

        pipe.connect("file_type_router.application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "docx_converter.sources")
        pipe.connect("file_type_router.application/msword", "doc_converter.sources")

        pipe.connect("file_type_router.application/vnd.ms-excel", "xls_converter.sources")
        pipe.connect("file_type_router.application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     "xlsx_converter.sources")
        pipe.connect("file_type_router.text/csv", "csv_converter.sources")

        pipe.connect("text_converter", "doc_joiner")
        pipe.connect("pdf_converter", "doc_joiner")
        pipe.connect("png_converter", "doc_joiner")
        pipe.connect("jpg_converter", "doc_joiner")
        pipe.connect("markdown_converter", "doc_joiner")
        pipe.connect("ppt_converter", "doc_joiner")
        pipe.connect("pptx_converter", "doc_joiner")
        pipe.connect("doc_converter", "doc_joiner")
        pipe.connect("docx_converter", "doc_joiner")
        pipe.connect("xls_converter", "doc_joiner")
        pipe.connect("xlsx_converter", "doc_joiner")
        pipe.connect("csv_converter", "doc_joiner")
        pipe.connect("doc_joiner", "splitter.documents")
        return pipe
