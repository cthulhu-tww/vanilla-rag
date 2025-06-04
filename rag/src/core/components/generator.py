import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Optional

from fastapi import Request
from openai import AsyncClient
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from src.core.entity.entity import OpenAiOptions, OllamaOptions
from src.core.util.mcp_util import MCPManager, TextResponse, FileResponse, BigTextResponse


class AbstractClient(ABC):

    def __init__(self):
        self.tool_list = []
        self.files = []

    @abstractmethod
    async def generate(self, messages, model=None, options=None):
        pass

    @abstractmethod
    async def generate_stream(self, messages, model=None, options=None, request: Request = None):
        pass

    @abstractmethod
    async def process_tools(self, chunk):
        pass

    @abstractmethod
    async def call_tools(self):
        pass


class OpenAIClient(AbstractClient):

    async def process_tools(self, chunk):
        tools_calls = []
        if hasattr(chunk.choices[0], 'message'):
            if chunk.choices[0].message.tool_calls is not None:
                tools_calls = chunk.choices[0].message.tool_calls

        elif hasattr(chunk.choices[0], "delta"):
            if chunk.choices[0].delta.tool_calls is not None:
                tools_calls = chunk.choices[0].delta.tool_calls

        if len(tools_calls) == 0:
            return

        for tool_call in tools_calls:
            index = tool_call.index
            while len(self.tool_list) <= index:
                self.tool_list.append({})
            if tool_call.id:
                self.tool_list[index]['id'] = self.tool_list[index].get('id', '') + tool_call.id
            if tool_call.function and tool_call.function.name:
                self.tool_list[index]['name'] = self.tool_list[index].get('name', '') + tool_call.function.name
            if tool_call.function and tool_call.function.arguments:
                self.tool_list[index]['arguments'] = self.tool_list[index].get('arguments',
                                                                               '') + tool_call.function.arguments

    async def call_tools(self):
        results = []
        if len(self.tool_list) > 0:
            for tool in self.tool_list:
                if tool.get('id') and tool.get('name'):
                    tool_id = tool['id']
                    tool_name = tool['name']
                    tool_arguments = tool.get('arguments', None)
                    response = await self.mcp_manager.call_tools(tool_name, tool_arguments)
                    c = ""
                    for r in response:
                        if isinstance(r, TextResponse):
                            c = c + r.text
                        elif isinstance(r, FileResponse):
                            c = c + "文件已保存，文件名：" + r.filename
                            self.files.append({
                                "filedata": r.data,
                                "filename": r.filename,
                                "mimetype": r.mimetype,
                            })
                        elif isinstance(r, BigTextResponse):
                            pass
                    results.append({"tool_call_id": tool_id, "content": c})

        return results

    def __init__(self, api_key, base_url, mcp_manager: MCPManager):
        super().__init__()
        if api_key is None or api_key == "":
            api_key = "..."
        self.client = AsyncClient(api_key=api_key, base_url=base_url)
        self.mcp_manager = mcp_manager

    async def generate(self, messages, model=None, options=None):
        _messages = deepcopy(messages)

        while True:
            self.tool_list = []
            r = await self.client.chat.completions.create(
                messages=_messages,
                extra_body={"enable_thinking": False},
                model=model,
                tools=self.mcp_manager.get_tools(),
                **options
            )

            content = r.choices[0].message.content
            if '</think>' in content:
                split = content.split('</think>')
                think = split[0].replace("<think>", "")
                content = split[1]
                r.choices[0].message.content = content
                r.choices[0].message.model_extra['reasoning_content'] = think

            await self.process_tools(r)
            if len(self.tool_list) > 0:
                results = await self.call_tools()
                tool_calls = []
                tools_message = []
                for (tool, result) in zip(self.tool_list, results):
                    tools_message.append({"role": "tool", "content": result["content"],
                                          "tool_call_id": result["tool_call_id"]})
                    tool_calls.append({
                        "id": tool['id'],
                        "function": {
                            "name": tool['name'],
                            "arguments": tool['arguments'],
                        },
                        "type": "function",
                    })
                _messages.append({"role": "assistant", "tool_calls": tool_calls})
                _messages.extend(tools_message)
                continue
            return r

    async def generate_stream(self, messages, model=None, options=None, request: Request = None):
        _messages = deepcopy(messages)
        try:
            while True:
                self.tool_list = []
                r = await self.client.chat.completions.create(
                    messages=_messages,
                    model=model,
                    extra_body={"enable_thinking": False},
                    stream=True,
                    tools=self.mcp_manager.get_tools(),
                    parallel_tool_calls=True,
                    **options
                )
                think_start = False
                think_end = False
                assistant_message = ''
                async for chunk in r:
                    await self.process_tools(chunk)
                    if len(self.tool_list) > 0:
                        yield "正在进行工具选择"
                        continue

                    if await request.is_disconnected():
                        r.response.close()
                        break
                    delta = chunk.choices[0].delta

                    if delta.content is None:
                        yield chunk
                        continue

                    if "<think>" in delta.content:
                        think_start = True
                        delta.model_extra['reasoning_content'] = delta.content.replace("<think>", "")
                        delta.content = None
                        yield chunk
                        continue

                    if "</think>" in delta.content:
                        think_end = True
                        delta.model_extra['reasoning_content'] = delta.content.replace("</think>", "")
                        delta.content = None
                        yield chunk
                        continue

                    if think_start and not think_end:
                        delta.model_extra['reasoning_content'] = delta.content
                        delta.content = None
                        yield chunk
                        continue
                    assistant_message = assistant_message + delta.content
                    yield chunk

                if len(self.tool_list) == 0:
                    break

                yield "正在调用工具"

                if assistant_message != "":
                    _messages.append({"role": "assistant", "content": assistant_message})

                results = await self.call_tools()
                tool_calls = []
                tools_message = []
                for (tool, result) in zip(self.tool_list, results):
                    tools_message.append({"role": "tool", "content": result["content"],
                                          "tool_call_id": result["tool_call_id"]})
                    tool_calls.append({
                        "id": tool['id'],
                        "function": {
                            "name": tool['name'],
                            "arguments": tool['arguments'],
                        },
                        "type": "function",
                    })
                _messages.append({"role": "assistant", "tool_calls": tool_calls})
                _messages.extend(tools_message)
        except Exception as e:
            print(e)
            yield create_response_from_str(str(e))

    def _openai_response_convert_ollama(self, chunk: ChatCompletion):
        return {
            "model": chunk.model,
            "created_at": chunk.created,
            "message": chunk.choices[0].message.__dict__,
            "done": chunk.choices[0].finish_reason is not None,
        }

    def _openai_response_convert_ollama_stream(self, chunk: ChatCompletionChunk):
        return {
            "model": chunk.model,
            "created_at": chunk.created,
            "message": {
                "role": chunk.choices[0].delta.role or "",
                "content": chunk.choices[0].delta.content
            },
            "done": chunk.choices[0].finish_reason is not None,
        }


class Generator:

    def _init_clients(self):
        """Initialize client strategy based on client type"""
        strategies = {
            # 'ollama': OllamaClient,
            'openai': OpenAIClient,
        }
        strategy_class = strategies.get(self.client_type)
        if not strategy_class:
            raise ValueError(f"Unsupported client type: {self.client_type}")
        self.client = strategy_class(api_key=self.api_key, base_url=self.base_url, mcp_manager=self.mcp_manager)

    def _init_system_prompt(self, system_prompt: Optional[str]):
        official_prompt = """
            请注意，你的回答应当保持官方、中立、严谨，避免使用过于激进或情绪化的语言。
            在回答问题时，务必基于事实和数据，避免主观臆断。
            对于不确定的信息，应当明确表示不确定性，并建议用户参考官方渠道获取准确信息。
            在涉及政策、法规等敏感话题时，应当严格遵守相关政策，避免误导用户。
            """
        self.system_prompt = official_prompt
        if system_prompt:
            self.system_prompt += f"\n{system_prompt}\n"

    def __init__(self,
                 client_type="openai",
                 api_key="",
                 base_url="",
                 system_prompt: str = None,
                 options: [OpenAiOptions | OllamaOptions] = None,
                 mcp_manager=None
                 ):
        if client_type not in ["ollama", "openai"]:
            raise ValueError("Unknown client type")
        self.client_type = client_type
        self.api_key = api_key
        self.base_url = base_url
        self.options = {} if options is None else options.model_dump()
        self.mcp_manager = mcp_manager
        self._init_clients()
        self._init_system_prompt(system_prompt)

    async def generate(self, messages: list[dict], model=None):
        if model is None:
            raise ValueError("model is None")

        if messages[0]['role'] == 'system':
            messages[0]['content'] = self.system_prompt
        else:
            messages.insert(0, {'role': 'system', 'content': self.system_prompt})

        r = await self.client.generate(messages=messages, model=model, options=self.options)
        if isinstance(r, str):
            return create_response_from_str(string=r, files=self.client.files)

        return create_response_from_chunk(chunk=r, files=self.client.files)

    async def generate_stream(self, messages, model=None, documents=None, request: Request = None):
        if model is None:
            yield create_response_from_str("模型参数错误，请联系管理员")
            raise ValueError("model is None")

        if messages[0]['role'] == 'system':
            messages[0]['content'] = self.system_prompt
        else:
            messages.insert(0, {'role': 'system', 'content': self.system_prompt})

        r = self.client.generate_stream(messages=messages, model=model,
                                        options=self.options,
                                        request=request)
        async for chunk in r:
            if isinstance(chunk, str):
                yield create_response_from_str(chunk)
                continue

            if chunk.choices[0].finish_reason is not None:
                yield create_response_from_chunk(chunk, reference=documents if documents else None,
                                                 files=self.client.files)
                continue

            yield create_response_from_chunk(chunk)


def create_response_from_str(string: str, step_content=True, done=False, files: list[dict] = None):
    return json.dumps({
        "model": None,
        "created_at": None,
        "message": {
            "role": "assistant",
            "content": string
        },
        "done": done,
        "reference": None,
        "step_content": step_content,
        "files": files
    }
    ) + "\n"


def create_response_from_chunk(chunk: ChatCompletion | ChatCompletionChunk, step_content=False, reference=None,
                               files: list[dict] = None):
    """
    role="assistant", string: str = None, think: str = None, step_content=True, done=False,
                               file=None,
                               filename=None

    """
    if isinstance(chunk, ChatCompletion):
        return {
            "message": {
                "role": chunk.choices[0].message.role,
                "content": chunk.choices[0].message.content,
                "think": chunk.choices[0].message.model_extra["reasoning_content"] if "reasoning_content" in
                                                                                      chunk.choices[
                                                                                          0].message.model_extra else None
            },
            "done": chunk.choices[0].finish_reason is not None,
            "reference": [r.__dict__ for r in reference] if reference else None,
        }

    delta = chunk.choices[0].delta
    return json.dumps({
        "message": {
            "role": delta.role,
            "content": delta.content,
            "think": delta.model_extra["reasoning_content"] if "reasoning_content" in delta.model_extra else None
        },
        "done": chunk.choices[0].finish_reason is not None,
        "reference": [r.__dict__ for r in reference] if reference else None,
        "step_content": step_content,
        "files": files,
    }, ensure_ascii=False,
    ) + "\n"
