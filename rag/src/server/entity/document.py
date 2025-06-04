from src.server.entity.common import ApplyTable, fields
from tortoise.models import Model


class DocumentModel(ApplyTable):
    """
    文档模型类
    """
    name = fields.CharField(max_length=255, description="文档名称")
    path = fields.CharField(max_length=255, description="文档路径")
    size = fields.IntField(description="文档大小,kb")
    mime_type = fields.CharField(max_length=50, description="文档类型")
    folder_id = fields.IntField(description="文件夹Id，关联文件夹表")

    class Meta:
        table = "sys_document"
        table_description = "文档表"
        # 单字段索引
        indexes = ("folder_id",)


class KnowledgeDocumentModel(Model):
    """
    知识库文档中间模型类
    """
    id = fields.IntField(pk=True, description="主键")
    k_id = fields.IntField(description="知识库id，关联知识库表")
    d_id = fields.IntField(description="文档id，关联文档表")
    status_text = fields.CharField(description="状态描述", max_length=255, null=True)
    status_code = fields.SmallIntField(description=" 0:排队中 1.解析中 2.解析失败 3.解析成功 4.未解析", default=4)
    source_id = fields.CharField(description="向量库源id", max_length=255, null=True)
    split_length = fields.IntField(description="分割长度")
    split_overlap = fields.IntField(description="分割重叠")

    class Meta:
        table = "sys_knowledge_document"
        table_description = "知识库文档中间表"
        indexes = (
            ("k_id",),  # 单字段索引
            ("d_id",),  # 单字段索引
            ("k_id", "d_id")  # 复合索引
        )
