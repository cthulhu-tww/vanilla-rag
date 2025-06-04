import hashlib
from typing import List

from fastapi import Request
from haystack import AsyncPipeline, Document
from haystack.components.builders import PromptBuilder
from haystack.components.converters import TextFileToDocument, MarkdownToDocument, CSVToDocument
from haystack.components.joiners import DocumentJoiner
from haystack.components.routers import FileTypeRouter

from src.core.components.generator import Generator, create_response_from_str
from src.core.components.pdf_to_document import PdfToDocument
from src.core.components.ppt_to_document import PptToDocument
from src.core.components.retriever import Retriever
from src.core.components.word_to_document import WordToDocument
from src.core.components.xlsx import XLSXToDocumentUpgrade
from src.core.entity.entity import Message, Params, RetrieverConfig
from src.core.entity.entity import Reference
from src.server.entity import ChatFilesModel
from src.server.service.knowledge import get_documents_by_sourceIds


async def router(context: List[Message], params: Params, request: Request):
    yield create_response_from_str("验证参数")
    try:
        llm = Generator(client_type=params.llm_config.api_type, api_key=params.llm_config.api_key,
                        base_url=params.llm_config.base_url, options=params.llm_config.options,
                        system_prompt=params.llm_config.system_prompt,
                        mcp_manager=request.app.state.mcp_manager)
        system_prompt = params.llm_config.system_prompt
        model = params.llm_config.model
        collection_name = params.retriever_config.collection_name
        open_rag = params.retriever_config.open_rag
        reference = [item for obj in context for item in obj.references]
        if (collection_name is None or len(collection_name) == 0) and open_rag:
            yield create_response_from_str("要启用RAG功能，请先选择对应的知识库")
            return

    except Exception as e:
        yield create_response_from_str(str(e))
        return

    files = [item for obj in context for item in obj.files]

    if len(files) > 0:
        async for c in file_chat(context=context,
                                 reference=reference,
                                 llm=llm,
                                 model=model,
                                 request=request):
            yield c
        return

    if not open_rag:
        async for c in chat(context, reference, llm, system_prompt, model, request):
            yield c
        return

    async for c in rag_chat(context=context,
                            reference=reference,
                            llm=llm,
                            model=model,
                            collection_name=collection_name,
                            retriever_config=params.retriever_config,
                            request=request):
        yield c


async def chat(context: List[Message], reference: list[Reference], llm: Generator, prompt: str, model: str, request):
    """
    不开启RAG 直接问答
    """

    context.insert(0, Message(role="system", content=prompt))
    async for chunk in llm.generate_stream(messages=[await c._dict()
                                                     for c in context], documents=reference, request=request,
                                           model=model):
        yield chunk


async def rag_chat(context: List[Message],
                   reference: list[Reference],
                   llm: Generator,
                   model: str,
                   retriever_config: RetrieverConfig,
                   collection_name: list[str],
                   request: Request):
    # 去除多余的reference
    all_chat_index = [item.chat_index for item in context]
    reference = [item for item in reference if item.chat_index in all_chat_index]

    new_doc = []

    yield create_response_from_str("重写用户的查询")
    retriever = await Retriever(context=context,
                                async_client=request.app.state.async_milvus_client,
                                client=request.app.state.milvus_client,
                                llm=llm,
                                model=model,
                                retriever_config=retriever_config
                                ).warm_up()
    documents = []

    yield create_response_from_str("向量检索")
    for index_name in collection_name:
        vector_documents = await retriever.vector_retrieval(index_name)
        documents.extend(vector_documents)

    metas = await get_documents_by_sourceIds(list(set(d.meta['source_id'] for d in documents)))
    for meta in metas:
        for doc in documents:
            if meta['source_id'] == doc.meta['source_id']:
                doc.meta['source_name'] = meta['source_name']
                doc.meta['create_time'] = meta['create_time'].strftime('%Y-%m-%d')

    # 去重过后的关联文档组装提示词，原reference不去重，保证每个文档关联一个question
    new_doc.extend([
        Reference(id=str(doc.id), content=doc.content, meta=doc.meta, score=doc.rerank_score,
                  chat_index=context[-1].chat_index,
                  hash=hashlib.md5(doc.content.encode('utf-8')).hexdigest())
        for doc in documents])

    yield create_response_from_str(f"检索结束，检索出{len(new_doc)}个文档，开始生成")

    # 检索出的文档，给到llm之前需要去重
    temp_references = set_reference_if_not_exist(reference, new_doc)
    # 检索出的文档给到前端则正常展示
    reference.extend(new_doc)
    context = _build_messages(context, temp_references)
    async for chunk in llm.generate_stream(messages=[await c._dict()
                                                     for c in context], documents=_clean_reference_response(new_doc),
                                           request=request,
                                           model=model):
        yield chunk


def analysis_pipe():
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
                                            "text/csv"
                                            ]), name="file_type_router")

    pipe.add_component("text_converter", TextFileToDocument())
    pipe.add_component("pdf_converter", PdfToDocument())
    pipe.add_component("markdown_converter", MarkdownToDocument())
    pipe.add_component("ppt_converter", PptToDocument())
    pipe.add_component("pptx_converter", PptToDocument())
    pipe.add_component("doc_converter", WordToDocument())
    pipe.add_component("docx_converter", WordToDocument())
    pipe.add_component("xls_converter", XLSXToDocumentUpgrade(table_format="markdown"))
    pipe.add_component("xlsx_converter", XLSXToDocumentUpgrade(table_format="markdown"))
    pipe.add_component("csv_converter", CSVToDocument())
    pipe.add_component("doc_joiner", DocumentJoiner())
    pipe.connect("file_type_router.text/plain", "text_converter.sources")
    pipe.connect("file_type_router.application/pdf", "pdf_converter.sources")
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
    pipe.connect("markdown_converter", "doc_joiner")
    pipe.connect("ppt_converter", "doc_joiner")
    pipe.connect("pptx_converter", "doc_joiner")
    pipe.connect("doc_converter", "doc_joiner")
    pipe.connect("docx_converter", "doc_joiner")
    pipe.connect("xls_converter", "doc_joiner")
    pipe.connect("xlsx_converter", "doc_joiner")
    pipe.connect("csv_converter", "doc_joiner")
    return pipe


async def file_chat(context: List[Message], reference: list[Reference], llm: Generator,
                    model: str, request):
    """文档问答"""
    files = await ChatFilesModel.filter(
        uuid__in=[file['uuid'] for file in context[-1].files if
                  not file['mimetype'].startswith('image')]).values()

    docs = [Document(content=file['content'], meta={"file_name": file['file_name']}) for file in files]

    new_references = [
        Reference(id=str(doc.id), content=doc.content, meta=doc.meta,
                  chat_index=context[-1].chat_index,
                  hash=hashlib.md5(doc.content.encode('utf-8')).hexdigest())
        for doc in docs]

    temp_references = set_reference_if_not_exist(reference, new_references)
    context = _build_messages(context, temp_references)
    async for chunk in llm.generate_stream(messages=[await c._dict()
                                                     for c in context],
                                           documents=_clean_reference_response(new_references),
                                           request=request, model=model):
        yield chunk


def _clean_reference_response(reference: list[Reference]):
    """清理文档给到前端，去掉多余的meta信息"""
    for r in reference:
        meta = {}
        for key in r.meta:
            if key not in ["sparse_vector", "page_number", "file_path", "split_id", "split_idx_start", "text",
                           "vector"]:
                meta[key] = r.meta[key]

        r.meta = meta

    return reference


def _build_messages(context, references):
    temp = """
    用户输入所参考文档内容:
    {% for document in documents %}      
    第{{ loop.index }}个文档
    文档名称: 《{{document.meta['file_name']}}》                                         
    {{ document.content }}\n\n
    {% endfor %}
    """

    prompt_builder = PromptBuilder(template=temp)
    prompt = prompt_builder.run(template_variables={"documents": references})[
        'prompt']
    context.insert(0, Message(role="assistant", content="上面文档作为参考来源"))
    context.insert(0, Message(role="user", content=prompt))
    return context


def set_reference_if_not_exist(origin, target):
    """根据文档内容hash去重"""
    result = []
    seen_hashes = set()

    for obj in origin:
        hash = obj.hash
        if hash not in seen_hashes:
            result.append(obj)
            seen_hashes.add(hash)

    # 遍历对象列表并根据哈希值去重
    for obj in target:
        hash = obj.hash

        # 如果哈希值未出现过，则将对象加入 unique_objects 数组，并记录哈希值
        if hash not in seen_hashes:
            result.append(obj)
            seen_hashes.add(hash)

    return result
