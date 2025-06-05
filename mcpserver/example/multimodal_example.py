import base64
import os
import platform
import subprocess
import uuid
from tempfile import NamedTemporaryFile
import markdown

IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    # 如果不是 Windows，导入 weasyprint 模块（只在 Linux/macOS 下）
    from weasyprint import HTML


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
