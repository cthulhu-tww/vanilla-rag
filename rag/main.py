import asyncio

import uvicorn
from fastapi import FastAPI
from pymilvus import AsyncMilvusClient, MilvusClient
from tortoise import Tortoise

from src.core.config import config
from src.core.milvus_manage import init_stores
from src.core.router.rag_base_router import router as rag_router
from src.core.util.mcp_util import MCPManager
from src.server.core.exceptions import exception_handlers
from src.server.core.middleware import middlewares
from src.server.router.auth import router as auth_router
from src.server.router.chat import router as chat_router
from src.server.router.document import router as document_router
from src.server.router.knowledge import router as knowledge_router

app = FastAPI(
    title="rag",
    version="0.1.0",
    middleware=middlewares,
    exception_handlers=exception_handlers,
)

milvus_client = MilvusClient(
    uri=f"http://{config.milvus['host']}:{config.milvus['port']}"
)

app.include_router(auth_router)
app.include_router(knowledge_router)
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(rag_router)


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
