import base64
import datetime
import os
import platform
import random
import subprocess
import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile

import markdown
import mysql.connector
import pollinations
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Tsingzhan-mcp", stateless_http=True, json_response=True, host="127.0.0.1", port=8880)

# server.py
from decimal import Decimal, getcontext, InvalidOperation

IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    # 如果不是 Windows，导入 weasyprint 模块（只在 Linux/macOS 下）
    from weasyprint import HTML


@mcp.tool()
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


@mcp.tool()
def get_exchange_rate(local_currency: str, foreign_currency: str) -> str:
    import requests
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


@mcp.tool()
def markdown_to_pdf(content: str, filename: str) -> dict:
    """接受一个markdown文本内容，将其渲染成pdf，并返回，可用于生成各式报告，离职单，请假单等等
    参数:
    content (str): markdown文本内容
    filename (str): 不带后缀名的文件名称

    返回:
        pdf文件
    """

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown to PDF</title>
        </head>
        <body>
        {markdown.markdown(content, extensions=['markdown.extensions.tables'])}
        </body>
        </html>
        """

    if IS_WINDOWS:
        # Windows：使用 weasyprint.exe 命令行方式
        with NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_html:
            tmp_html.write(html_content)
            tmp_html_path = tmp_html.name

        output_pdf = uuid.uuid4().hex + ".pdf"

        try:
            weasyprint_exe = "weasyprint.exe"
            subprocess.run([weasyprint_exe, tmp_html_path, output_pdf], check=True)

            with open(output_pdf, "rb") as f:
                file_data = f.read()

            base64_file_data = base64.b64encode(file_data).decode("utf-8")

            return {
                "type": "file",
                "filename": f"{filename}.pdf",
                "mimetype": "application/pdf",
                "data": base64_file_data
            }

        finally:
            for path in [tmp_html_path, output_pdf]:
                if os.path.exists(path):
                    os.unlink(path)

    else:
        # Linux 或 macOS：使用 weasyprint Python 库直接生成 PDF
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()

        base64_file_data = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "type": "file",
            "filename": f"{filename}.pdf",
            "mimetype": "application/pdf",
            "data": base64_file_data
        }

@mcp.tool()
def text_2_image(prompt: str, image_name: str, width: int = 1024, height: int = 1024, seed: int = None) -> dict:
    """
    将提示词转换为图片，并返回图片文件。

    参数:
        prompt (str): 要转换的文本内容，必须为英文
        image_name (str): 不带后缀的图片名称
        width (int): 图片宽度
        height (int): 图片高度
        seed (int): 0-100000，不传默认随机

    返回:
        FileContent: 包含图片数据的 FileContent 对象
    """
    from pollinations import ImageModel
    if seed is None:
        seed = random.randint(0, 100000)

    model = pollinations.Image(
        model=ImageModel(name="flux"),
        width=width,
        height=height,
        seed=seed,
        nologo=True
    )
    pil_image = model.Generate(
        prompt=prompt,
        save=False
    )
    img_byte_stream = BytesIO()
    pil_image.save(img_byte_stream, format="JPEG")
    img_byte_stream.seek(0)
    filedata_base64 = base64.b64encode(img_byte_stream.read()).decode("utf-8")
    return {
        "type": "file",
        "filename": f"{image_name}.jpg",
        "mimetype": "image/jpeg",
        "data": f"data:image/jpeg;base64,{filedata_base64}"
    }


@mcp.tool()
def now() -> str:
    """获取用户本地实时时间"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
