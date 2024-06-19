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
    convert: bool,
    translate: bool = False,
) -> str:
    """
    Convert pdf file to specified file
    """
    # Upload the file and get uuid
    try:
        uuid = await upload_pdf(
            apikey=apikey, pdffile=pdf_path, ocr=ocr, translate=translate
        )
    except RateLimit:
        # Retry according to maxretry and current rpm
        for i in range(maxretry):
            print(f"Reach the rate limit, wait for {60 // rpm} seconds")
            await asyncio.sleep(60 // rpm)
            try:
                print(f"Retrying {i+1} / {maxretry} times")
                uuid = await upload_pdf(apikey=apikey, pdffile=pdf_path, ocr=ocr)
            except RateLimit:
                if i == maxretry - 1:
                    raise RuntimeError(
                        "Reach the max retry times, but still get rate limit"
                    )
                continue
    # Wait for the process to finish
    while True:
        status_process, status_str, texts, other = await uuid_status(
            apikey=apikey, uuid=uuid, convert=convert, translate=translate
        )
        if status_process == 100 and status_str == "Success" and not translate:
            # If output_format is texts, return texts directly
            if output_format == "texts":
                return texts
            break
        elif status_process == 100 and status_str == "Translate success":
            return texts
        print(f"{status_str}: {status_process}%")
        await asyncio.sleep(1)
    # Convert uuid to file
    return await uuid2file(
        apikey=apikey, uuid=uuid, output_path=output_path, output_format=output_format
    )


async def img2file_v1(
    apikey: str,
    img_path: str,
    output_path: str,
    output_format: str,
    formula: bool,
    img_correction: bool,
    maxretry: int,
    rpm: int,
    convert: bool,
) -> str:
    """
    Convert image file to specified file, async version
    """
    try:
        uuid = await upload_img(
            apikey=apikey,
            imgfile=img_path,
            formula=formula,
            img_correction=img_correction,
        )
    except RateLimit:
        # Retry according to maxretry and current rpm
        for i in range(maxretry):
            print(f"Reach the rate limit, wait for {60 // rpm} seconds")
            await asyncio.sleep(60 // rpm)
            try:
                print(f"Retrying {i+1} / {maxretry} times")
                uuid = await upload_img(
                    apikey=apikey,
                    imgfile=img_path,
                    formula=formula,
                    img_correction=img_correction,
                )
            except RateLimit:
                if i == maxretry - 1:
                    raise RuntimeError(
                        "Reach the max retry times, but still get rate limit"
                    )
                continue
    # Wait for the process to finish
    while True:
        status_process, status_str, texts, other = await uuid_status(
            apikey=apikey, uuid=uuid, convert=convert
        )
        if status_process == 100 and status_str == "Success":
            # If output_format is texts, return texts directly
            if output_format == "texts":
                return texts
            break
        print(f"{status_str}: {status_process}%")
        await asyncio.sleep(1)
    return await uuid2file(
        apikey=apikey, uuid=uuid, output_path=output_path, output_format=output_format
    )


class Doc2X:
    """
    `apikey`: Your apikey, or get from environment variable `DOC2X_APIKEY`
    `rpm`: Request per minute, default is `4`
    `thread`: Max thread number, default is `1`
    `maxretry`: Max retry times, default is `3`
    """

    def __init__(
        self, apikey: str = "", rpm: int = 4, thread: int = 1, maxretry: int = 3
    ) -> None:
        self.apikey = asyncio.run(get_key(apikey))
        self.limiter = AsyncLimiter(rpm, 60)
        self.rmp = rpm
        self.threadnum = asyncio.Semaphore(thread)
        self.maxretry = maxretry

    async def pic2file_back(
        self,
        image_file: str,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        img_correction: bool = True,
        equation=False,
        convert: bool = False,
    ) -> str:
        """
        Convert image file to specified file, with rate/thread limit
        """
        async with self.limiter:
            async with self.threadnum:
                return await img2file_v1(
                    apikey=self.apikey,
                    img_path=image_file,
                    output_path=output_path,
                    output_format=output_format,
                    formula=equation,
                    img_correction=img_correction,
                    maxretry=self.maxretry,
                    rpm=self.rmp,
                    convert=convert,
                )

    def pic2file(
        self,
        image_file: str,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        img_correction: bool = True,
        equation=False,
        convert: bool = False,
    ) -> str:
        """
        Convert image file to specified file
        `image_file`: image file path
        `output_path`: output folder path, default is "./Output"
        `output_format`: output format, accept `texts`, `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`
        `img_correction`: whether to correct the image, default is `True`
        `equation`: whether the image is an equation, default is `False`
        `convert`: whether to convert `[` to `$` and `[[` to `$$`, default is False

        return: output file path
        """
        return asyncio.run(
            self.pic2file_back(
                image_file,
                output_path,
                output_format,
                img_correction,
                equation,
                convert,
            )
        )

    async def pdf2file_back(
        self,
        pdf_file: str,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
        translate: bool = False,
    ) -> str:
        """
        Convert pdf file to specified file, with rate/thread limit, async version
        """
        async with self.limiter:
            async with self.threadnum:
                return await pdf2file_v1(
                    apikey=self.apikey,
                    pdf_path=pdf_file,
                    output_path=output_path,
                    output_format=output_format,
                    ocr=ocr,
                    maxretry=self.maxretry,
                    rpm=self.rmp,
                    convert=convert,
                    translate=translate,
                )

    def pdf2file(
        self,
        pdf_file: str,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
    ) -> str:
        """
        Convert pdf file to specified file
        `pdf_file`: pdf file path
        `output_path`: output folder path, default is "./Output"
        `output_format`: output format, accept `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`

        return: output file path
        """
        return asyncio.run(
            self.pdf2file_back(
                pdf_file, output_path, output_format, ocr, convert, False
            )
        )
