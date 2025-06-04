import os
import uuid
from datetime import datetime
from pathlib import Path

FILE_PATH = "./files"
KNOWLEDGE_FILE_FOLDER = "knowledge"
CHAT_FILE_FOLDER = "chat"


async def upload(data: bytes, filename: str, folder_name: str = KNOWLEDGE_FILE_FOLDER) -> str:
    if not filename:
        raise ValueError("Uploaded file has no filename")
    today_str = datetime.now().strftime("%Y-%m-%d")
    file_path = Path(FILE_PATH) / today_str / folder_name
    file_path.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename).suffix
    uuid_name = f"{uuid.uuid4()}{suffix}"
    full_path = file_path / uuid_name

    with open(full_path, "wb") as buffer:
        buffer.write(data)

    return str(full_path)


async def remove_files(files_path: []):
    if not files_path:
        return
    for file_path in files_path:
        path = Path(file_path)
        if path.exists():
            path.unlink()


async def get_file(path: str) -> bytes:
    """
    异步读取文件并返回其完整字节内容。

    :param path: 文件路径
    :return: 文件的完整字节内容（bytes），如果文件不存在或无法读取则返回空 bytes
    """
    if not path or not os.path.isfile(path):
        return b''  # 返回空字节对象作为默认值

    try:
        with open(path, "rb") as f:
            return f.read()  # 返回完整的字节内容
    except Exception as e:
        return b''
