from typing import Optional

from pydantic import BaseModel, Field

from src.core.entity.entity import LLMConfig


class ChatHistoryBasic(BaseModel):
    title: str = Field(None, description="标题")
    message_content: Optional[str] = Field(None, description="聊天记录内容")


class ChatHistoryIn(ChatHistoryBasic):
    id: int = Field(None, description="聊天记录的主键ID")
    export_type: int = Field(None, description="导出类型")
    llm_config: LLMConfig = Field(None, description="LLM配置")
    pass


class ChatHistoryTitleOut(BaseModel):
    id: int = Field(..., description="聊天记录的主键ID")
    title: str = Field(..., description="聊天记录的标题")


class ChatHistoryContentOut(BaseModel):
    id: int = Field(..., description="聊天记录的主键ID")
    message_content: str = Field(..., description="聊天记录的内容")
