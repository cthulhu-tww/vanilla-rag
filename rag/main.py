import asyncio
import os

import uvicorn
from fastapi import FastAPI
from pymilvus import AsyncMilvusClient, MilvusClient
from tortoise import Tortoise

from src.core.config import config
from src.core.milvus_manage import init_stores
from src.core.util.mcp_util import MCPManager
from src.server.core.exceptions import exception_handlers
from src.server.core.middleware import middlewares
from src.server.core.utils import load_routers

current_dir = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(
    title="rag",
    version="0.1.0",
    middleware=middlewares,
    exception_handlers=exception_handlers,
)

milvus_client = MilvusClient(
    uri=f"http://{config.milvus['host']}:{config.milvus['port']}"
)

# 动态构建 package_path 中的路径
package_paths = [
    os.path.join(current_dir, "src", "server", "router"),
    os.path.join(current_dir, "src", "core", "router")
]

load_routers(app=app, package_path=package_paths)


@app.on_event("startup")
async def startup_event():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["src.server.entity"]},
        use_tz=False,
        timezone="Asia/Shanghai",
    )
    await Tortoise.generate_schemas()
    app.state.milvus_client = MilvusClient(
        uri=f"http://{config.milvus['host']}:{config.milvus['port']}"
    )
    app.state.async_milvus_client = AsyncMilvusClient(
        uri=f"http://{config.milvus['host']}:{config.milvus['port']}"
    )
    await init_stores()
    from src.core.components.analysis_task import task
    asyncio.create_task(task.run())
    mcp_manager = MCPManager(config.mcp["url"])
    if config.mcp["enable"]:
        asyncio.create_task(mcp_manager.refresh())
    app.state.mcp_manager = mcp_manager


@app.on_event("shutdown")
async def shutdown_event():
    await Tortoise.close_connections()


if __name__ == "__main__":
    uvicorn.run(app, host=config.server["host"], port=config.server["port"], reload=False)
