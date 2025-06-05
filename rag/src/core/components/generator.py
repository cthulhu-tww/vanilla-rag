import json
from abc import ABC, abstractmethod
from copy import deepcopy

from fastapi import Request
from openai import AsyncClient
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from src.core.entity.entity import OpenAiOptions, OllamaOptions
from src.core.util.mcp_util import MCPManager, TextResponse, FileResponse, BigTextResponse


class AbstractClient(ABC):

    def __init__(self):
        self.tool_list = []
        self.files = []
        self.system_prompt = ""

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

    def __init__(self, api_key, base_url, mcp_manager: MCPManager, system_prompt: str = ""):
        super().__init__()
        if api_key is None or api_key == "":
            api_key = "..."
        self.client = AsyncClient(api_key=api_key, base_url=base_url)
        self.mcp_manager = mcp_manager

        self.system_prompt = system_prompt

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

    async def generate(self, messages, model=None, options=None):
        if messages[0]['role'] == 'system':
            messages[0]['content'] = self.system_prompt
        else:
            messages.insert(0, {'role': 'system', 'content': self.system_prompt})
        _messages = deepcopy(messages)

        while True:
            self.tool_list = []
            r = await self.client.chat.completions.create(
                messages=_messages,
                extra_body={"enable_thinking": False},
                model=model,
                tools=self.mcp_manager.get_tools(),
                **options if options else {}
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
        if messages[0]['role'] == 'system':
            messages[0]['content'] = self.system_prompt
        else:
            messages.insert(0, {'role': 'system', 'content': self.system_prompt})
        _messages = deepcopy(messages)

        r = await self.generate(messages=[
            {
                "role": "user",
                "content": f"""{[f"{m['role']}:{m['content']}" for m in messages]}
                       请判断上述需求，是否需要调用工具，如果需要请返回：[[yes]]，如果不需要请返回：[[no]]
                       """
            }
        ], model=model)
        user_tools = False
        if "[[yes]]" in r.choices[0].message.content:
            user_tools = True
            _messages[-1]["content"] = f"""
                             用户需求：
                             {_messages[-1]["content"]}
                             #你必须按照以下步骤思考：
                             1. 分析问题本质
                             2. 检查可用工具及其适用场景
                             3. 评估各工具的优势劣势
                             4. 选择最匹配的工具
                             5. 验证选择的合理性
                             6. 考虑工具的关联，是否有工具为前置工具
                             7. 确定工具执行顺序
                             8. 如果达不到预期，你需要进行反思，考虑可能解决的方案。
                             """

        try:
            while True:
                self.tool_list = []
                r = await self.client.chat.completions.create(
                    messages=_messages,
                    model=model,
                    extra_body={"enable_thinking": False},
                    stream=True,
                    tools=self.mcp_manager.get_tools() if user_tools else None,
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

                if len(self.tool_list) == 0 or '[[done]]' in assistant_message:
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
            yield e


class Generator:

    def _init_clients(self, mcp_manager: MCPManager, system_prompt: str = ""):
        """Initialize client strategy based on client type"""
        strategies = {
            # 'ollama': OllamaClient,
            'openai': OpenAIClient,
        }
        strategy_class = strategies.get(self.client_type)
        if not strategy_class:
            raise ValueError(f"Unsupported client type: {self.client_type}")
        self.client = strategy_class(api_key=self.api_key, base_url=self.base_url, mcp_manager=mcp_manager,
                                     system_prompt=system_prompt)

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
        preset_prompt = """
        你是一个安全、中立且负责任的AI助手。在回答用户问题时，请严格遵守以下准则：  
        1. **禁止讨论政治敏感话题**：包括但不限于国家主权、领土完整、意识形态争议、国内外政治事件等。  
        2. **避免偏激或煽动性内容**：不发表任何可能引发对立、歧视、仇恨或暴力倾向的言论。  
        3. **过滤NSFW内容**：不涉及色情、暴力、犯罪指导等违反法律法规或道德规范的内容。  
        4. **保持客观中立**：对争议性话题（如宗教、种族、性别等）需基于事实陈述，不表达主观倾向。  
        5. **拒绝非法或有害请求**：如用户提问涉及违法操作（如黑客攻击、制造危险品等），必须明确拒绝并提醒其合法性。  

        若用户问题触及上述限制，你应礼貌回应：  
        『抱歉，我无法协助完成该请求。请遵守法律法规，并确保内容安全、健康。』  
        你的首要任务是提供有益、无害且符合社会价值观的帮助。
        """
        self._init_clients(mcp_manager, system_prompt=f"""
        {preset_prompt}
        {system_prompt}
        """)

    async def generate(self, messages: list[dict], model=None):
        if model is None:
            raise ValueError("model is None")
        r = await self.client.generate(messages=messages, model=model, options=self.options)
        if isinstance(r, str):
            return create_response_from_str(string=r, files=self.client.files)

        return create_response_from_chunk(chunk=r, files=self.client.files)

    async def generate_stream(self, messages, model=None, documents=None, request: Request = None):
        if model is None:
            yield create_response_from_str("模型参数错误，请联系管理员")
            return

        r = self.client.generate_stream(messages=messages, model=model,
                                        options=self.options,
                                        request=request)
        async for chunk in r:
            if isinstance(chunk, str):
                yield create_response_from_str(chunk)
                continue

            if chunk.choices[0].finish_reason is not None:
                yield create_response_from_chunk(chunk, reference=documents if documents else None,
                                                 step_content=False,
                                                 files=self.client.files)
                continue

            yield create_response_from_chunk(chunk, step_content=False)


def create_response_from_str(string: str, step_content=True, done=False, files: list[dict] = None):
    return json.dumps({
        "message": {
            "role": "assistant",
            "content": string
        },
        "done": done,
        "reference": None,
        "step_content": step_content,
        "files": files
    }, ensure_ascii=False) + "\n"


def create_response_from_chunk(chunk: ChatCompletion | ChatCompletionChunk, step_content=True, reference=None,
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
    }, ensure_ascii=False) + "\n"
