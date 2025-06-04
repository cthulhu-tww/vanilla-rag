import importlib.util
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def load_routers(
        app,
        package_path: [str] = "router",
        router_name: str = "router",
        no_depends="common",
        depends: list = None,
):
    """
    自动注册路由
    :param app: FastAPI 实例对象 或者 APIRouter对象
    :param package_path: 路由包所在路径，默认相对路径router包
    :param router_name: APIRouter实例名称，需所有实例统一，默认router
    :param is_init: 是否在包中的__init__.py中导入了所有APIRouter实例，默认否
    :param no_depends: 不需要依赖注入的模块（py文件）名，默认common
    :param depends: 依赖注入列表 默认为None
    :return: 默认None
    """
    if no_depends is None:
        no_depends = []

    def __register(module_obj):
        """注册路由，module_obj： 模块对象"""
        if hasattr(module_obj, router_name):
            router_obj = getattr(module_obj, router_name)
            # if any(nd in module_obj.__name__ for nd in no_depends):  # 该代码是通过字符串进行匹配，从而排除指定的模块，可能导致问题
            # 获取模块的文件名（不含扩展名）
            module_file_name = os.path.splitext(os.path.basename(module_obj.__file__))[0]
            if module_file_name in no_depends:
                kwargs = dict(router=router_obj)
            else:
                kwargs = dict(router=router_obj, dependencies=depends)
            app.include_router(**kwargs)

    logger.info("♻️开始扫描路由。")
    if depends is None:
        depends = []

    # 获取目录下所有的 Python 文件（去除 .py 后缀）
    for path in package_path:
        modules = [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']

        for module in modules:
            module_file = os.path.join(path, f"{module}.py")
            if not os.path.isfile(module_file):
                logger.warning(f"模块文件不存在: {module_file}")
                continue

            spec = importlib.util.spec_from_file_location(f"{module}", module_file)
            if spec and spec.loader:
                module_obj = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module_obj)
                    __register(module_obj)
                    logger.info(f"已注册模块: {module_obj.__name__}")
                except Exception as e:
                    raise e
            else:
                logger.error(f"无法创建模块规范: {module_file}")

    for route in app.routes:
        try:
            logger.info(
                f"🦌{route.path}, {route.methods}, {route.__dict__.get('summary')}"
            )
        except AttributeError as e:
            logger.error(e)
    logger.info("®️路由注册完成✅。")


# 自定义 JSON 编码器
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # 转换为 ISO 格式的字符串
        return super(DateTimeEncoder, self).default(obj)
