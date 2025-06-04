from typing import Any, Dict, Union, Literal

from pydantic import BaseModel


class OllamaOptions(BaseModel):
    """ollama api 采样参数 自行扩展"""
    temperature: float = 0.7


class OpenAiOptions(BaseModel):
    """openai api 采样参数 自行扩展"""
    temperature: float = 0.7
    max_tokens: int = 4096


class LLMConfig(BaseModel):
    system_prompt: str = ""  # 系统提示
    base_url: str = "https://api.deepseek.com/v1"  # 模型供应商api地址
    api_key: str = ""  # 模型供应商api key
    model: str = "deepseek-chat"  # 模型名称
    api_type: Literal["openai", "vllm", "ollama"] = "openai"  # 模型类型，vllm 会判断上下文长度
    options: Union[OpenAiOptions, OllamaOptions]


class RetrieverConfig(BaseModel):
    collection_name: list[str] = []  # 知识库ids
    open_rag: bool = True  # 开启检索增强生成，开启时知识库id必填
    retriever_top_k: int = 20  # 检索召回数量
    rerank_top_k: int = 20  # 重排召回数量
    rerank_similarity_threshold: float = 0.5  # 重排相似度阈值
    keyword_weight: float = 0.5  # 关键词权重


class Params(BaseModel):
    llm_config: LLMConfig
    retriever_config: RetrieverConfig


class Reference(BaseModel):
    chat_index: str = ""  # 文档和问题的绑定索引
    id: str = ""
    content: str = ''
    url: str = ''
    meta: Dict[str, Any] = {}
    score: float = 0.0
    hash: str = ""


class Message(BaseModel):
    chat_index: str = ""
    role: str
    content: str
    files: list[dict] = []
    references: list[Reference] = []

    async def _dict(self):
        return {
            "content": self.content,
            "role": self.role,
        }
