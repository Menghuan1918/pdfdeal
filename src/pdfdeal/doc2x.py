import asyncio
import os
from typing import Tuple, List
import logging
from .Doc2X.ConvertV2 import upload_pdf, uid_status, convert_parse, get_convert_result
from .Doc2X.Exception import RequestError, RateLimit
from .FileTools.dealpdfs import strore_pdf


async def pdf2file(
    apikey: str,
    pdf_path: str,
    output_path: str,
    output_format: str,
    ocr: bool,
    maxretry: int,
    wait_time: int,
    max_time:int,
    convert: bool,
) -> str:
    """
    Convert pdf file to specified file using V2 API
    """
    try:
        uid = await upload_pdf(apikey, pdf_path, ocr)
    except RateLimit:
        for _ in range(maxretry):
            await asyncio.sleep(wait_time)
            try:
                uid = await upload_pdf(apikey, pdf_path, ocr)
                break
            except RateLimit:
                continue
        else:
            raise RequestError("Max retry reached for upload_pdf")

    for _ in range(max_time):
        progress, status, texts, locations = await uid_status(apikey, uid, convert)
        if status == "Success":
            if output_format == "texts":
                return texts
            elif output_format in ["md", "tex", "docx"]:
                status, url = await convert_parse(apikey, uid, output_format)
                while status == "Processing":
                    await asyncio.sleep(1)
                    status, url = await get_convert_result(apikey, uid)
                if status == "Success":
                    return url
            elif output_format == "pdf":
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                strore_pdf(output_path, texts)
                return output_path
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        elif status == "Processing file":
            logging.info(f"Processing: {progress}%")
            await asyncio.sleep(1)
        else:
            raise RequestError(f"Unexpected status: {status}")
    raise RequestError("Max time reached for uid_status")


class Doc2X:
    def __init__(self, apikey: str = None, retry_time: int = 15, max_time: int = 120) -> None:
        self.apikey = apikey or os.environ.get("DOC2X_APIKEY", "")
        if not self.apikey:
            raise ValueError("No apikey found")
        self.retry_time = retry_time
        self.max_time = max_time

    async def pdf2file_back(
        self,
        pdf_file: List[str],
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
    ) -> Tuple[List[str], List[dict], bool]:
        limit = asyncio.Semaphore(self.rpm)

        async def process_file(pdf):
            async with limit:
                try:
                    result = await pdf2file(
                        apikey=self.apikey,
                        pdf_path=pdf,
                        output_path=os.path.join(output_path, os.path.basename(pdf)),
                        output_format=output_format,
                        ocr=ocr,
                        wait_time=15,
                        convert=convert,
                    )
                    return result, "", True
                except Exception as e:
                    return "", str(e), False

        results = await asyncio.gather(*[process_file(pdf) for pdf in pdf_file])

        success_files = [r[0] if r[2] else "" for r in results]
        failed_files = [
            {"error": r[1], "path": pdf} if not r[2] else {"error": "", "path": ""}
            for r, pdf in zip(results, pdf_file)
        ]
        has_error = any(not r[2] for r in results)

        return success_files, failed_files, has_error

    def pdf2file(self, *args, **kwargs):
        return asyncio.run(self.pdf2file_back(*args, **kwargs))
