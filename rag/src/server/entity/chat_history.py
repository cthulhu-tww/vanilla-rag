from src.server.entity.common import fields, ApplyTable


class LongTextField(fields.TextField):
    SQL_TYPE = "LONGTEXT"


class ChatHistoryModel(ApplyTable):
    """
    聊天记录模型类
    """
    title = fields.CharField(max_length=255, description="聊天记录标题")
    message_content = LongTextField(description="聊天记录内容")
    uid = fields.IntField(description="用户Id，关联用户表", index=True)

    class Meta:
        table = "sys_chat_history"
        table_description = "聊天记录表"


class ChatFilesModel(ApplyTable):
    """
    聊天记录文件模型类
    """
    file_name = fields.CharField(max_length=255, description="文件名")
    file_path = fields.CharField(max_length=768, description="文件路径", index=True)
    mime_type = fields.CharField(max_length=255, description="文件类型")
    uuid = fields.CharField(max_length=255, description="文件uuid")
    content = LongTextField(description="文件内容", default=None, null=True)
    size = fields.FloatField(description="文件大小 kb")

    class Meta:
        table = "sys_chat_files"
        table_description = "聊天记录文件表"
