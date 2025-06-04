from src.server.entity.common import fields, ApplyTable


class KnowledgeModel(ApplyTable):
    """
    知识库模型类
    """
    label = fields.CharField(max_length=255, description="标签")
    name = fields.CharField(max_length=255, description="知识库名称")
    description = fields.CharField(max_length=255, null=True, description="描述")
    index_name = fields.CharField(max_length=255, description="索引名称")
    create_by = fields.IntField(max_length=20, null=True, default=0, description="创建人，如果没有就为0")

    class Meta:
        table = "sys_knowledge"
        table_description = "知识库表"
        # 单字段索引
        indexes = ("name",)


