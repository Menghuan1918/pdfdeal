import httpx
import json
import os
import re
from typing import Tuple, Literal
from .Exception import RateLimit

Base_URL = "https://api.doc2x.noedgeai.com/api"


async def refresh_key(key: str) -> str:
    """
    Get new key by refresh key
    """
    url = f"{Base_URL}/token/refresh"
    timeout = httpx.Timeout(30)
    async with httpx.AsyncClient(timeout=timeout) as client:
        get_res = await client.post(url, headers={"Authorization": "Bearer " + key})
    if get_res.status_code == 200:
        return json.loads(get_res.content.decode("utf-8"))["data"]["token"]
    else:
        raise Exception(f"Refresh key error! {get_res.status_code}:{get_res.text}")


async def check_folder(path: str) -> bool:
    """
    检查输入的是否为文件夹，是则保证文件夹存在并返回True,否则抛出异常
    """
    try:
        os.makedirs(path, exist_ok=True)
        assert os.path.isdir(path)
    except FileExistsError:
        raise Exception("Input path already exists as a file!")
    except NotADirectoryError:
        raise Exception("Input path is not a directory!")
    except Exception as e:
        raise Exception(f"Create folder error! {e}")
    return True


async def uuid2file(
    apikey: str,
    uuid: str,
    output_format: Literal["md", "md_dollar", "latex", "docx"],
    output_path: str = "./Output",
) -> str:
    """
    用于获取文件，输入：
    `apikey`: key
    `uuid`: 文件uuid
    `output_format`: 输出格式
    `output_path`: 输出文件夹路径

    返回：
    `str`：输出文件路径
    """
    # 检查输出路径并拼接url，纠正下载的文件格式
    await check_folder(output_path)
    url = f"{Base_URL}/export?request_id={uuid}&to={output_format}"
    download_format = output_format if output_format == "docx" else "zip"
    timeout = httpx.Timeout(120)
    async with httpx.AsyncClient(timeout=timeout) as client:
        get_res = await client.get(url, headers={"Authorization": "Bearer " + apikey})
    if get_res.status_code == 200:
        output_path = os.path.join(output_path, uuid + "." + download_format)
        try:
            with open(output_path, "wb") as f:
                f.write(get_res.content)
            return output_path
        except Exception as e:
            raise Exception(f"Dowload file error! {e}")
    else:
        if get_res.status_code == 429:
            raise RateLimit()
        else:
            raise Exception(
                f"Download file error! {get_res.status_code}:{get_res.text}"
            )


async def get_limit(apikey: str) -> int:
    """
    获取剩余可用的次数

    输入：
    `apikey`: key

    返回：
    `int`：剩余次数
    """
    if apikey.startswith("sk-"):
        url = f"{Base_URL}/v1/limit"
    else:
        url = f"{Base_URL}/platform/limit"
    async with httpx.AsyncClient() as client:
        get_res = await client.get(url, headers={"Authorization": "Bearer " + apikey})
    if get_res.status_code == 200:
        return int(get_res.json()["data"]["remain"])
    else:
        raise RuntimeError(f"Get limit error! {get_res.status_code}:{get_res.text}")


async def upload_pdf(
    apikey: str,
    pdffile: str,
    ocr: bool = True,
    translate: bool = False,
) -> str:
    """
    上传pdf文件到服务器，返回文件的uuid

    输入：
    `apikey`: key
    `pdffile`: pdf文件路径
    `ocr`: 是否使用ocr，默认为True
    `translate`: 是否翻译，默认为False

    返回：
    `str`：文件的uuid
    """
    if apikey.startswith("sk-"):
        url = f"{Base_URL}/v1/async/pdf"
    else:
        url = f"{Base_URL}/platform/async/pdf"
    try:
        file = {"file": open(pdffile, "rb")}
    except Exception as e:
        raise Exception(f"Open file error! {e}")
    ocr = 1 if ocr else 0
    translate = 2 if translate else 1
    timeout = httpx.Timeout(120)
    async with httpx.AsyncClient(timeout=timeout) as client:
        post_res = await client.post(
            url,
            headers={"Authorization": "Bearer " + apikey},
            files=file,
            data={"ocr": ocr, "parse_to": translate},
        )
    if post_res.status_code == 200:
        return json.loads(post_res.content.decode("utf-8"))["data"]["uuid"]
    elif post_res.status_code == 429:
        raise RateLimit()
    else:
        raise Exception(f"Upload file error! {post_res.status_code}:{post_res.text}")


async def upload_img(
    apikey: str,
    imgfile: str,
    formula: bool = False,
    img_correction: bool = False,
) -> str:
    """
    上传图片文件到服务器，返回文件的uuid
    输入：
    `apikey`: key
    `imgfile`: 图片文件路径
    `formula`: 是否返回纯公式，默认为False
    `img_correction`: 是否进行图片校正，默认为False

    返回：
    `str`：文件的uuid
    """
    if apikey.startswith("sk-"):
        url = f"{Base_URL}/v1/async/img"
    else:
        url = f"{Base_URL}/platform/async/img"
    formula = 1 if formula else 0
    img_correction = 1 if img_correction else 0
    try:
        file = {"file": open(imgfile, "rb")}
    except Exception as e:
        raise Exception(f"Open file error! {e}")
    timeout = httpx.Timeout(120)
    async with httpx.AsyncClient(timeout=timeout) as client:
        post_res = await client.post(
            url,
            headers={"Authorization": "Bearer " + apikey},
            files=file,
            data={"option": formula, "img_correction": img_correction},
        )
    if post_res.status_code == 200:
        return json.loads(post_res.content.decode("utf-8"))["data"]["uuid"]
    elif post_res.status_code == 429:
        raise RateLimit()
    else:
        raise Exception(f"Upload file error! {post_res.status_code}:{post_res.text}")


async def decode_data(datas: json, convert: bool) -> Tuple[list, list]:
    """
    用于解码基本数据
    """
    texts = []
    locations = []
    for data in datas["result"]["pages"]:
        try:
            text = data["md"]
        except KeyError:
            text = ""
        if convert:
            text = re.sub(r"\\[()]", "$", text)
            text = re.sub(r"\\[\[\]]", "$$", text)
        try:
            url = data["url"]
        except KeyError:
            url = ""
        # When processing image, there is no page_idx
        try:
            page_id = data["page_idx"]
        except KeyError:
            page_id = 0
        location = {
            "url": url,
            "page_idx": page_id,
            "page_width": data["page_width"],
            "page_height": data["page_height"],
        }
        texts.append(text)
        locations.append(location)
    return texts, locations


async def decode_translate(datas: json, convert: bool) -> Tuple[list, list]:
    """
    用于解码翻译数据
    """
    texts = []
    locations = []
    Rawinput = json.loads(datas["result"])
    for data in Rawinput:
        try:
            text = data["raw"]
            translate_text = data["translated"]
            if convert:
                text = re.sub(r"\\[()]", "$", text)
                text = re.sub(r"\\[\[\]]", "$$", text)
                translate_text = re.sub(r"\\[()]", "$", translate_text)
                translate_text = re.sub(r"\\[\[\]]", "$$", translate_text)
            location = {
                "raw_text": text,
                "page_idx": data["page_idx"],
                "page_width": data["page_width"],
                "page_height": data["page_height"],
                "x": data["x"],
                "y": data["y"],
            }
            texts.append(translate_text)
            locations.append(location)
        except KeyError:
            continue
    return texts, locations


async def uuid_status(
    apikey: str,
    uuid: str,
    convert: bool = False,
    translate: bool = False,
) -> Tuple[int, str, list]:
    """
    获取文件的状态和转换后的uuid

    输入：
    `apikey`: key
    `uuid`: 文件uuid
    `convert`: 是否转换"["和"[["到"$""$$"，默认为False
    `translate`: 是否翻译，默认为False

    返回：
    `Tuple[int, str, list, list]`: 转换进度，当前状态，转换后的文本列表，文本坐标列表
    """
    if apikey.startswith("sk-"):
        url = f"{Base_URL}/v1/async/status?uuid={uuid}"
    else:
        url = f"{Base_URL}/platform/async/status?uuid={uuid}"
    if translate:
        url += "&parse_to=2"
    timeout = httpx.Timeout(30)
    async with httpx.AsyncClient(timeout=timeout) as client:
        get_res = await client.get(url, headers={"Authorization": "Bearer " + apikey})
    if get_res.status_code == 200:
        datas = json.loads(get_res.content.decode("utf-8"))["data"]
        if datas["status"] == "ready":
            return 0, "Waiting for processing", [], []

        elif datas["status"] == "processing":
            return int(datas["progress"]), "Processing file", [], []

        elif datas["status"] == "translate_processing":
            return int(datas["progress"]), "Translating file", [], []

        elif datas["status"] == "success":
            texts, locations = await decode_data(datas, convert)
            return 100, "Success", texts, locations

        elif datas["status"] == "translate_success":
            texts, locations = await decode_translate(datas, convert)
            return 100, "Translate success", texts, locations

        elif datas["status"] == "pages limit exceeded":
            raise RuntimeError("Pages limit exceeded!")

        else:
            raise RuntimeError(f"Unknown status! {datas['status']}")

    raise Exception(f"Get status error! {get_res.status_code}:{get_res.text}")
