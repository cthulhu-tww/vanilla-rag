from fastapi import APIRouter

from src.server.schemas import common as BaseSchema
from src.server.service import auth as AuthService

router = APIRouter(tags=["公共"])

LoginResult = BaseSchema.Response[BaseSchema.LoginResult]


@router.post("/api/login", summary="登录")
async def login(data: BaseSchema.LoginForm) -> LoginResult:
    return await AuthService.user_login(data)


@router.post("/api/register", summary="注册")
async def register(data: BaseSchema.LoginForm) -> LoginResult:
    return await AuthService.register(data)