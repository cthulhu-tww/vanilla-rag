from typing import Optional, List

from pydantic import BaseModel, Field

from rag.src.server.schemas.common import QueryData, ReadBase


class UserBasic(BaseModel):
    username: Optional[str] = Field(None, description="账户名称，登录用")
    nickname: str = Field(..., description="昵称，登录或展示用")
    password: Optional[str] = Field(None, description="密码")
    department_id: int = Field(..., description="部门编号")


class UserIn(UserBasic):
    rid: int = Field(..., description="权限id")
    id: Optional[int] = Field(None, description="主键")
    pass


class UserRead(UserBasic, ReadBase):
    pass


class UserHasRole(BaseModel):
    """用户拥有角色"""

    id: int
    name: str
    status: int = Field(default=1, description="激活角色 5 正常 1 删除 9")


class UserInfo(UserRead):
    """用户信息模型"""

    roles: List[UserHasRole] = Field(..., description="用户拥有角色")


class RoleActive(BaseModel):
    rid: int = Field(description="角色id")
    status: int = Field(default=1, description="激活角色 5 正常 1 删除 9")


class UserAdd(UserIn):
    """新增用户模型"""

    roles: List[RoleActive] = Field(..., description="选择角色列表")


class UserQuery(QueryData):
    """查询模型"""

    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="姓名")
    department_name: Optional[str] = Field(None, description="部门")
    ids: Optional[list[int]] = Field([], description="id")


class UserPut(BaseModel):
    """用户更新模型"""

    nickname: str = Field(..., description="用户昵称")
    roles: List[RoleActive] = Field(..., description="选择角色列表")


class UserChangeOwnPass(BaseModel):
    """用户更新自己的密码"""

    oldPassword: str = Field(..., description="旧密码")
    newPassword: str = Field(..., description="新密码")


class Department(BaseModel):
    name: str = Field(None, description="部门名称")


class DepartmentIn(Department):
    id: Optional[int] = Field(None, description="主键")
    pass


class DepartmentQuery(QueryData):
    name: str = Field(None, description="部门名称")


class WebsearchAPI(BaseModel):
    id: int = Field(..., description="用户Id")
    websearchAPI: Optional[str] = Field(None, description="网络搜索API")
