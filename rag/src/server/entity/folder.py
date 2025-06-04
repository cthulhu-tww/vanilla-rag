from src.server.entity.common import fields, ApplyTable


class FolderModel(ApplyTable):
    """
    文件夹模型类
    """
    name = fields.CharField(max_length=255, description="文件夹名")
    create_by = fields.IntField(default=0, description="创建人")

    class Meta:
        table = "sys_folder"
        table_description = "文件夹表"
        # 唯一索引
        unique_together = ("name",)
