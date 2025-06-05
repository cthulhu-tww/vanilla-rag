import base64
import random
from io import BytesIO


def text_2_image(prompt: str, image_name: str, width: int = 1024, height: int = 1024, seed: int = None) -> dict:
    import pollinations
    from pollinations import ImageModel
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
