import json
from datetime import datetime
from io import BytesIO

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist

from src.server.entity import ChatHistoryModel
from src.core.components.generator import Generator
from src.server.schemas.chat_history import ChatHistoryIn, ChatHistoryTitleOut, ChatHistoryContentOut
from src.server.schemas.common import QueryData, ListAll
import pandas as pd

from fastapi import Response

ChatHistory_Pydantic = pydantic_model_creator(ChatHistoryModel, name="ChatHistory")
ChatHistoryIn_Pydantic = pydantic_model_creator(ChatHistoryModel, name="ChatHistoryIn", exclude_readonly=True)


async def create_chat_history(chat_history: ChatHistoryIn, uid: int, request):
    if chat_history.title is None or chat_history.title == "":
        llm = Generator(client_type=chat_history.llm_config.api_type, api_key=chat_history.llm_config.api_key,
                        base_url=chat_history.llm_config.base_url, mcp_manager=request.app.state.mcp_manager)
        context = json.loads(chat_history.message_content)
        context.append({
            "role": "user",
            "content": "根据以上用户问题以及助手答复，给出一个标题，标题内容最多8个中文。"
        })

        res = await llm.generate([{'role': c['role'], 'content': c['content']} for c in context],
                                 model=chat_history.llm_config.model)
        title = res['message']['content']
        ds = json.loads(chat_history.message_content)
        chat_history.title = ds[0]['content']
        chat_history.title = title

    if chat_history.id is None or chat_history.id <= 0:
        # 如果没有 ID 或 ID 无效，视为新记录
        chat_history_dict = chat_history.dict(exclude={"id"})
        chat_history_instance = await ChatHistoryModel.create(uid=uid, **chat_history_dict)
    else:
        # 尝试通过 ID 找到已有记录
        existing_chat_history = await ChatHistoryModel.get_or_none(id=chat_history.id)
        if existing_chat_history:
            # 如果找到，更新记录
            chat_history_dict = chat_history.dict(exclude_unset=True)  # 只更新提供的字段
            for key, value in chat_history_dict.items():
                setattr(existing_chat_history, key, value)
            await existing_chat_history.save()
            chat_history_instance = existing_chat_history
        else:
            chat_history_dict = chat_history.dict(exclude={"id"})
            chat_history_instance = await ChatHistoryModel.create(uid=uid, **chat_history_dict)

    return {"id": chat_history_instance.id, "title": chat_history.title}


async def get_chat_history_titles(uid: int, query: QueryData) -> ListAll[ChatHistoryTitleOut]:
    total = await ChatHistoryModel.filter(uid=uid).count()
    chat_history_objs = await ChatHistoryModel.filter(uid=uid).order_by('-created').offset(
        (query.offset - 1) * query.limit).limit(query.limit)

    chat_history_data_list = [
        ChatHistoryTitleOut(id=obj.id, title=obj.title) for obj in chat_history_objs
    ]

    return ListAll(total=total, items=chat_history_data_list)


async def get_chat_history_content(record_id: int) -> ChatHistoryContentOut:
    try:
        record = await ChatHistoryModel.get_or_none(id=record_id)
    except DoesNotExist:
        raise ValueError("Chat history not found")
    return ChatHistoryContentOut(id=record.id, message_content=record.message_content)


async def delete_chat_history(record_id: int):
    try:
        record = await ChatHistoryModel.get(id=record_id)
    except DoesNotExist:
        raise ValueError("Chat history not found")
    await record.delete()


async def clear(user_id: int):
    await ChatHistoryModel.filter(uid=user_id).delete()


async def export(export_type, message_content):
    if export_type == 0:
        context = json.loads(message_content)
        text = []
        stream = BytesIO()
        for c in context:
            if c['role'] == 'user':
                text.append("\n------------ user ------------\n")
            elif c['role'] == 'assistant':
                text.append("\n------------ assistant ------------\n")
            elif c['role'] == 'system':
                text.append("\n------------ system ------------\n")
            text.append(c['content'])

        text_str = "".join(text)
        stream.write(text_str.encode('utf-8'))
        stream.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d")}_export.txt"'
        }

        # 返回 txt 文件内容作为响应
        return Response(content=stream.read(), media_type='text/plain', headers=headers)

    if export_type == 1:
        context = json.loads(message_content)
        df = pd.DataFrame({
            'Name': [c['role'] for c in context],
            'Content': [c['content'] for c in context]
        })
        stream = BytesIO()
        df.to_csv(stream, index=False, encoding='utf-8-sig')
        stream.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d")}_export.csv"'
        }

        # 返回 CSV 文件内容作为响应
        return Response(content=stream.read(), media_type='text/csv', headers=headers)

    if export_type == 2:
        context = json.loads(message_content)
        text = []
        stream = BytesIO()
        for c in context:
            if c['role'] == 'user':
                text.append("\n### user\n")
            elif c['role'] == 'assistant':
                text.append("\n### assistant\n")
            elif c['role'] == 'system':
                text.append("\n### system\n")
            text.append(c['content'])

        text_str = "".join(text)
        stream.write(text_str.encode('utf-8'))
        stream.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d")}_export.md"'
        }

        # 返回 markdown 文件内容作为响应
        return Response(content=stream.read(), media_type='application/json', headers=headers)

    if export_type == 3:
        context = json.loads(message_content)
        stream = BytesIO()
        stream.write(json.dumps(context, ensure_ascii=False, indent=4).encode('utf-8'))
        stream.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d")}_export.json"'
        }

        # 返回 json 文件内容作为响应
        return Response(content=stream.read(), media_type='application/json', headers=headers)


async def update_title(chat_history: ChatHistoryIn):
    return await ChatHistoryModel.filter(id=chat_history.id).update(title=chat_history.title)
