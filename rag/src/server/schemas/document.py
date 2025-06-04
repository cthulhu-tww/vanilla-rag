from typing import Optional, List

from pydantic import Field, BaseModel

from src.server.schemas.common import DTOBase, CustomBaseModel


class DocumentBasic(CustomBaseModel):
    id: int = Field(..., description="文档ID")
    name: str = Field(..., description="文档名称")
    path: str = Field(..., description="文档路径")
    size: int = Field(..., description="文档大小,kb")
    mime_type: str = Field(..., description="文档类型")


class DocumentIn(DocumentBasic):
    pass


class DocumentOut(DocumentBasic, DTOBase):
    pass


class DocumentClassification(BaseModel):
    k_id: int = Field(..., description="知识库ID")
    d_ids: List[int] = Field(..., description="文档ID")
    classification: int = Field(..., description="文件处理分类，默认为1：通用，2：表格（隐藏配置选项）")


class KnowledgeDocumentOut(DocumentBasic, DTOBase):
    status_code: int = Field(..., description="解析状态，默认为1：未解析，2：解析成功，3：解析失败，4：解析中")
    status_text: str = Field(..., description="解析状态描述")
    split_length: int = Field(..., description="分割长度")
    split_overlap: int = Field(..., description="分割重叠")


class FolderBasic(CustomBaseModel):
    name: Optional[str] = Field("", description="文件夹名")
    owner_type: int = Field(default=2, description="0 所有人可见  1 部分人可见 2 仅自己可见")


class FolderIn(FolderBasic):
    id: Optional[int] = Field(0, description="文件夹id")
    owner_ids: list = Field([], description="归属者")
    pass


class FolderOut(FolderBasic, DTOBase):
    has_permission: bool = Field(default=False, description="是否有权限")
    pass


class FolderSimple(FolderBasic):
    id: int = Field(..., description="文件夹Id")


class FolderWithDocumentsOut(BaseModel):
    folder: FolderSimple
    documents: List[DocumentBasic]


class SplitSetting(BaseModel):
    knowledgeId: int = Field(..., description="知识库ID")
    documentIds: List[int] = Field(..., description="文件Id集合")
    split_length: int = Field(..., description="分割长度")
    split_overlap: int = Field(..., description="分割重叠")


class DocumentSetting(BaseModel):
    knowledge_id: int = Field(..., description="知识库ID")
    document_id: int = Field(..., description="文件Id")


class DocumentAnalysis(BaseModel):
    knowledge_id: int = Field(..., description="知识库Id")
    documentIds: List[int] = Field(..., description="文件Id集合")


class UploadWebContent(BaseModel):
    urls: List[str] = Field(..., description="网络资源URL")
    folder_id: int = Field(..., description="文件夹ID")
