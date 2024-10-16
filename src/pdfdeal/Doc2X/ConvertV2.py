import httpx
import json
import os
import re
from typing import Tuple
from .Exception import RateLimit, FileError, RequestError, async_retry
import logging

Base_URL = "https://v2.doc2x.noedgeai.com/api"


@async_retry()
async def get_limit(apikey: str) -> Tuple[int, int, int, int]:
    """Get the quota information of the key

    Args:
        apikey (str): The key

    Raises:
        RuntimeError: The key is invalid or there's an error in the response

    Returns:
        Tuple[int, int, int, int]: A tuple containing (remain, quota, used_pages, free_pages)
    """
    url = f"{Base_URL}/v2/user/quota"
    async with httpx.AsyncClient() as client:
        get_res = await client.get(url, headers={"Authorization": f"Bearer {apikey}"})
    if get_res.status_code != 200:
        raise RuntimeError(
            f"Get quota information error! {get_res.status_code}:{get_res.text}"
        )
    try:
        data = get_res.json()["data"]
        return tuple(
            int(data[key]) for key in ["remain", "quota", "used_pages", "free_pages"]
        )
    except Exception as e:
        raise RuntimeError(
            f"Get quota information error with {e}! {get_res.status_code}:{get_res.text}"
        )


@async_retry()
async def upload_pdf(apikey: str, pdffile: str, ocr: bool = True) -> str:
    """Upload pdf file to server and return the uid of the file

    Args:
        apikey (str): The key
        pdffile (str): The pdf file path
        ocr (bool, optional): Do OCR or not. Defaults to True.

    Raises:
        FileError: Input file size is too large
        FileError: Open file error
        RateLimit: Rate limit exceeded
        Exception: Upload file error

    Returns:
        str: The uid of the file
    """
    url = f"{Base_URL}/v2/parse/pdf"
    if os.path.getsize(pdffile) >= 100 * 1024 * 1024:
        logging.warning("Now not support PDF file > 100MB!")
        raise FileError("Input file size is too large")
        logging.warning(
            "File size is too large, will auto switch to S3 file upload way, this may take a while"
        )
        return await upload_pdf_big(apikey, pdffile, ocr)

    try:
        with open(pdffile, "rb") as f:
            file = f.read()
    except Exception as e:
        raise FileError(f"Open file error! {e}")

    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
        post_res = await client.post(
            url,
            params={"ocr": str(ocr).lower()},
            headers={
                "Authorization": f"Bearer {apikey}",
                "Content-Type": "application/pdf",
            },
            content=file,
        )

    if post_res.status_code == 200:
        response_data = json.loads(post_res.content.decode("utf-8"))
        if response_data.get("code") == "parse_task_limit_exceeded":
            raise RateLimit()
        return response_data["data"]["uid"]

    if post_res.status_code == 429:
        raise RateLimit()
    if post_res.status_code == 400:
        raise RequestError(post_res.text)

    raise Exception(f"Upload file error! {post_res.status_code}:{post_res.text}")


@async_retry()
async def upload_pdf_big(apikey: str, pdffile: str, ocr: bool = True) -> str:
    """Upload big pdf file(>100m) to server and return the uid of the file

    Args:
        apikey (str): The key
        pdffile (str): The pdf file path
        ocr (bool, optional): Do OCR or not. Defaults to True.

    Raises:
        FileError: Input file size is too large
        FileError: Open file error
        RateLimit: Rate limit exceeded
        Exception: Upload file error

    Returns:
        str: The uid of the file
    """
    if os.path.getsize(pdffile) < 100 * 1024 * 1024:
        raise FileError("PDF file size should be bigger than 100MB!")

    try:
        file = {"file": open(pdffile, "rb")}
    except Exception as e:
        raise FileError(f"Open file error! {e}")

    url = f"{Base_URL}/v2/parse/preupload"
    filename = os.path.basename(pdffile)[:20]
    timeout = httpx.Timeout(120)

    async with httpx.AsyncClient(timeout=timeout) as client:
        post_res = await client.post(
            url,
            headers={"Authorization": f"Bearer {apikey}"},
            json={"file_name": filename, "ocr": ocr},
        )

    if post_res.status_code == 200:
        response_data = json.loads(post_res.content.decode("utf-8"))
        if response_data.get("code") != "ok":
            raise RequestError(post_res.text)

        upload_data = response_data["data"]
        upload_url = upload_data["url"]
        uid = upload_data["form"]["x-amz-meta-uid"]

        async with httpx.AsyncClient(timeout=timeout) as client:
            s3_res = await client.post(
                url=upload_url,
                data=upload_data["form"],
                files=file,
            )
        if s3_res.status_code == 204:
            return uid
        else:
            raise RequestError(s3_res.text)
    if post_res.status_code == 429:
        raise RateLimit()
    if post_res.status_code == 400:
        raise RequestError(post_res.text)
    raise Exception(f"Upload file error! {post_res.status_code}:{post_res.text}")


async def decode_data(data: dict, convert: bool) -> Tuple[list, list]:
    """Decode the data

    Args:
        data (dict): The response data
        convert (bool): Convert "[" and "[[" to "$" and "$$"

    Returns:
        Tuple[list, list]: The texts and locations
    """
    texts = []
    locations = []
    if "result" not in data or "pages" not in data["result"]:
        logging.warning("Although parsed successfully, the content is empty!")
        return [], []
    texts, locations = [], []
    for page in data["result"]["pages"]:
        text = page.get("md", "")
        if convert:
            text = re.sub(r"\\[()]", "$", text)
            text = re.sub(r"\\[\[\]]", "$$", text)
        texts.append(text)
        locations.append(
            {
                "url": page.get("url", ""),
                "page_idx": page.get("page_idx", 0),
                "page_width": page.get("page_width", 0),
                "page_height": page.get("page_height", 0),
            }
        )
    return texts, locations


@async_retry()
async def uid_status(
    apikey: str,
    uid: str,
    convert: bool = False,
) -> Tuple[int, str, list, list]:
    """Get the status of the file

    Args:
        apikey (str): The key
        uid (str): The uid of the file
        convert (bool, optional): Convert "[" and "[[" to "$" and "$$" or not. Defaults to False.

    Raises:
        RequestError: Failed to deal with file
        Exception: Get status error

    Returns:
        Tuple[int, str, list, list]: The progress, status, texts and locations
    """
    url = f"{Base_URL}/v2/parse/status?uid={uid}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(30)) as client:
        get_res = await client.get(url, headers={"Authorization": f"Bearer {apikey}"})
    if get_res.status_code != 200:
        raise Exception(f"Get status error! {get_res.status_code}:{get_res.text}")

    try:
        data = json.loads(get_res.content.decode("utf-8"))
    except Exception as e:
        raise Exception(
            f"Get status error with {e}! {get_res.status_code}:{get_res.text}"
        )

    if data["code"] != "ok":
        raise RequestError(f"Failed to get status: {data.get('msg', 'Unknown error')}")

    progress, status = data["data"].get("progress", 0), data["data"].get("status", "")
    if status == "processing":
        return progress, "Processing file", [], []
    elif status == "success":
        texts, locations = await decode_data(data["data"], convert)
        return 100, "Success", texts, locations
    elif status == "failed":
        raise RequestError(f"Failed to deal with file! {get_res.text}")
    else:
        logging.warning(f"Unknown status: {status}")
        return progress, status, [], []
