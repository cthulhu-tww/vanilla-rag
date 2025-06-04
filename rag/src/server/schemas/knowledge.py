from typing import Optional

from pydantic import Field, validator

from src.server.schemas.common import DTOBase, CustomBaseModel


class KnowledgeBasic(CustomBaseModel):
    label: str = Field(description="知识库标签")
    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")

    @validator('name')
    def check_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('name cannot be an empty string')
        return v


class KnowledgeIn(KnowledgeBasic):
    id: Optional[int] = Field(0, description="知识库id")
    index_name: Optional[str] = Field(None, description="索引名称")
    pass


class KnowledgeOut(KnowledgeBasic, DTOBase):
    document_count: int = Field(..., description="知识库文档数")

