import httpx
import asyncio
from aiolimiter import AsyncLimiter
import json
import os
import zipfile
import time
import re
from .file_tools import texts_to_file
from typing import Tuple, Literal
from .Doc2X.Exception import RateLimit
from .Doc2X.Convert import (
    refresh_key,
    unzip,
    get_limit,
    uuid2file,
    upload_pdf,
    upload_img,
    uuid_status,
)


async def get_key(apikey: str) -> str:
    """
    从服务器获取新的key(不适用于sk开头的key)
    可从环境变量获得
    """
    if apikey is None:
        apikey = os.getenv("DOC2X_APIKEY", "")
    if apikey == "":
        raise ValueError("No apikey found")
    if not apikey.startswith("sk-"):
        apikey = await refresh_key(apikey)
    return apikey


# 一些常用功能的封装
async def pdf2file_v1(
    apikey: str,
    pdf_path: str,
    output_path: str,
    output_format: str,
    ocr: bool,
    maxretry: int,
    rpm: int,
) -> str:
    """
    将pdf文件转换为指定文件
    """
    try:
        uuid = await upload_pdf(apikey=apikey, pdffile=pdf_path, ocr=ocr)
    except RateLimit:
        # 根据maxretry以及当前的rpm等待时间重试
        for i in range(maxretry):
            await asyncio.sleep(60 // rpm)
            try:
                uuid = await upload_pdf(apikey=apikey, pdffile=pdf_path, ocr=ocr)
            except RateLimit:
                continue
    return await uuid2file(
        apikey=apikey, uuid=uuid, output_path=output_path, output_format=output_format
    )


class Doc2X:
    """
    输入：
    `apikey`: key，或者从环境变量`DOC2X_APIKEY`中获取
    `rpm`: 每分钟的请求次数，默认为4
    `thread`: 最大并发数，默认为1
    `maxretry`: 最大重试次数，默认为3
    """

    def __init__(
        self, apikey: str = "", rpm: int = 4, thread: int = 1, maxretry: int = 3
    ) -> None:
        self.apikey = asyncio.run(get_key(apikey))
        self.limiter = AsyncLimiter(rpm, 60)
        self.rmp = rpm
        self.threadnum = asyncio.Semaphore(thread)
        self.maxretry = maxretry
