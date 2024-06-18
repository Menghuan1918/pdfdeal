import httpx
import asyncio
import json
import os
import zipfile
import time
import re
from .file_tools import texts_to_file
from typing import Tuple, Literal
from .Doc2X.Exception import RateLimit

Base_URL = "https://api.doc2x.noedgeai.com/api"


async def refresh_key(key: str) -> str:
    """
    从服务器获取新的key(不使用于sk开头的key)
    """
    url = f"{Base_URL}/token/refresh"
    async with httpx.AsyncClient() as client:
        get_res = await client.post(url, headers={"Authorization": "Bearer " + key})
    if get_res.status_code == 200:
        return json.loads(get_res.content.decode("utf-8"))["data"]["token"]
    else:
        raise Exception(f"Refresh key error! {get_res.status_code}:{get_res.text}")


async def upload_pdf(zip_path: str) -> str:
    """
    用于创建响应文件夹并解压文件
    """
    folder_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_path = os.path.join(os.path.dirname(zip_path), folder_name)
    os.makedirs(extract_path, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        os.remove(zip_path)
        return extract_path
    except Exception as e:
        raise Exception(f"Unzip file error! {e}")


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
    return True


async def uuid2file(
    apikey: str,
    uuid: str,
    output_format: Literal["md", "md_dollar", "latex", "docx"],
    output_path: str = "./Output",
) -> str:
    """
    用于获取文件，入参：
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

    async with httpx.AsyncClient() as client:
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
            raise Exception(f"Download file error! {get_res.status_code}:{get_res.text}")