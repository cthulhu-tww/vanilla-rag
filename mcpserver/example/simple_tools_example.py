import datetime
from decimal import Decimal, getcontext, InvalidOperation


def decimal_calculate(a, b, operator, precision=10):
    """
    使用Decimal指定精度进行高精度金额小数计算，涉及到金额，必须调用此工具

    参数:
        a (str or float or int): 第一个操作数
        b (str or float or int): 第二个操作数
        operator (str): 运算符，支持 '+', '-', '*', '/'
        precision (int): 计算的精度（有效数字位数）

    返回:
        str: 计算结果字符串表示
    """
    # 设置全局精度
    getcontext().prec = int(precision)

    try:
        # 转换为 Decimal 类型
        a_dec = Decimal(str(a))
        b_dec = Decimal(str(b))

        # 根据运算符执行计算
        if operator == '+':
            result = a_dec + b_dec
        elif operator == '-':
            result = a_dec - b_dec
        elif operator == '*':
            result = a_dec * b_dec
        elif operator == '/':
            if b_dec == 0:
                return "错误：除数不能为零"
            result = a_dec / b_dec
        else:
            return f"错误：不支持的运算符 '{operator}'"

        # 返回格式化后的结果字符串
        return format(result.normalize(), 'f')  # 去掉无效的末尾0

    except InvalidOperation:
        return "错误：无效的操作数"
    except Exception as e:
        return f"发生错误：{e}"


def get_exchange_rate(local_currency: str, foreign_currency: str) -> str:
    """
    获取本地货币(local_currency)对外币(foreign_currency)的实时汇率。

    参数:
        local_currency (str): 本币标准交易代码（如 'CNY', 'USD'）
        foreign_currency (str): 外币标准交易代码（如 'USD', 'JPY'）

    返回:
        float: 汇率，表示 1 单位本币等于多少单位外币

    异常:
        ValueError: 如果货币代码无效或无法获取数据
        ConnectionError: 如果请求失败
    """
    import requests

    # 统一转为小写，API 接口要求路径是小写格式
    local = local_currency.lower()
    foreign = foreign_currency.lower()

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{local}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 检查是否包含所需的外币汇率
        if foreign not in data.get(local, {}):
            raise ValueError(f"无法找到 {foreign_currency} 的汇率数据")

        return f"1 {local_currency} = {data[local][foreign]} {foreign_currency}"

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"请求失败: {e}")
    except KeyError:
        raise ValueError("返回数据中缺少汇率信息")


def now() -> str:
    """获取用户本地实时时间"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
