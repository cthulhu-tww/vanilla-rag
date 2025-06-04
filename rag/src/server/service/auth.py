from fastapi import HTTPException

from src.server.core.dbhelper import has_user
from src.server.core.security import generate_token, verify_password, get_password_hash
from src.server.entity import UserModel


async def user_login(data):
    """用户登录"""
    user_obj = await has_user(data.username)
    if user_obj:
        if verify_password(data.password, user_obj.password):
            return dict(data=dict(id=user_obj.id, username=data.username, token=generate_token(data.username)))
    raise HTTPException(status_code=400, detail="账号或密码错误")


async def register(data):
    """用户注册"""
    user_obj = await has_user(data.username)
    if user_obj:
        raise HTTPException(status_code=400, detail="用户已存在")

    if len(data.username) < 3 or len(data.username) > 20:
        raise HTTPException(status_code=400, detail="用户名长度必须在3-20个字符之间")

    if len(data.password) < 6 or len(data.password) > 20:
        raise HTTPException(status_code=400, detail="密码长度必须在6-20个字符之间")

    await UserModel.create(username=data.username, password=get_password_hash(data.password))
    return dict(code=200, msg="注册成功", data=None)
