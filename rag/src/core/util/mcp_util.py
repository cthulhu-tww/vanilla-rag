import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import TextContent, ImageContent
from pydantic import BaseModel


class TextResponse(BaseModel):
    text: str

    def __str__(self):
        return self.text


class FileResponse(BaseModel):
    filename: str
    mimetype: str
    data: str


class BigTextResponse(BaseModel):
    text: str


def generate_response_from_text(text: str) -> [TextResponse | FileResponse | BigTextResponse]:
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            _type = obj.get("type")
            if _type == 'big_text':
                return BigTextResponse(text=text)
            if _type == 'file':
                return FileResponse(filename=obj["filename"], mimetype=obj["mimetype"], data=obj["data"])
    except json.JSONDecodeError:
        pass

    return BigTextResponse(text=text) if len(text) > 5000 else TextResponse(text=text)


class MCPManager:
    def get_tools(self):
        return None if len(self.tools) == 0 else self.tools

    def __init__(self, url: str):
        self.url = url
        self.tools = []

    async def refresh(self, minute=5):
        while True:
            await self.list_tools()
            await asyncio.sleep(60 * minute)

    async def list_tools(self):
        async with streamablehttp_client(f"{self.url}/mcp") as (
                read_stream,
                write_stream,
                _,):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                self.tools = self.get_openai_tools_dicts(response.tools)

    async def call_tools(self, tool_name, tool_arguments) -> list[TextResponse | FileResponse | BigTextResponse]:
        async with streamablehttp_client(f"{self.url}/mcp") as (
                read_stream,
                write_stream,
                _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.call_tool(tool_name, json.loads(tool_arguments))
                r: list[TextResponse | FileResponse | BigTextResponse] = []
                for content in response.content:
                    if isinstance(content, TextContent):
                        r.append(generate_response_from_text(content.text))
                    elif isinstance(content, ImageContent):
                        pass

                return r

    @staticmethod
    def get_openai_tools_dicts(tools):
        """获取openai api 兼容的工具调用格式"""
        return [{"type": "function", "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }} for tool in tools]
