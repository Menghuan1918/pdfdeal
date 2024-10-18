import asyncio
import os
from typing import Tuple, List
import logging
from .Doc2X.ConvertV2 import (
    upload_pdf,
    uid_status,
    convert_parse,
    get_convert_result,
    download_file,
)
from .Doc2X.Types import OutputFormat
from .Doc2X.Pages import get_pdf_page_count
from .Doc2X.Exception import RequestError, RateLimit, run_async
from .FileTools.file_tools import get_files
import warnings


async def pdf2file(
    apikey: str,
    pdf_path: str,
    output_path: str,
    output_format: str,
    output_name: str,
    ocr: bool,
    maxretry: int,
    wait_time: int,
    max_time: int,
    convert: bool,
) -> str:
    """Convert pdf file to specified file using V2 API"""

    async def retry_upload():
        for _ in range(maxretry):
            try:
                return await upload_pdf(apikey, pdf_path, ocr)
            except RateLimit:
                await asyncio.sleep(wait_time)
        raise RequestError("Max retry reached for upload_pdf")

    try:
        logging.info(f"Uploading {pdf_path}...")
        uid = await upload_pdf(apikey, pdf_path, ocr)
    except RateLimit:
        uid = await retry_upload()

    for _ in range(max_time):
        progress, status, texts, locations = await uid_status(apikey, uid, convert)
        if status == "Success":
            logging.info(f"Conversion successful for {pdf_path} with uid {uid}")
            if output_format == "texts":
                return texts
            elif output_format == "detailed":
                return [
                    {"text": text, "location": loc}
                    for text, loc in zip(texts, locations)
                ]
            elif output_format in ["md", "md_dollar", "tex", "docx"]:
                logging.info(f"Parsing {uid} to {output_format}...")
                status, url = await convert_parse(apikey, uid, output_format)
                for _ in range(max_time):
                    if status == "Success":
                        logging.info(f"Downloading {uid} to {output_path}...")
                        return await download_file(
                            url=url,
                            file_type=output_format,
                            target_folder=output_path,
                            target_filename=output_name or uid,
                        )
                    elif status == "Processing":
                        await asyncio.sleep(1)
                        status, url = await get_convert_result(apikey, uid)
                    else:
                        raise RequestError(f"Unexpected status: {status}")
                raise RequestError("Max time reached for get_convert_result")
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        elif status == "Processing file":
            logging.info(f"Processing {uid} : {progress}%")
            await asyncio.sleep(1)
        else:
            raise RequestError(f"Unexpected status: {status}")
    raise RequestError("Max time reached for uid_status")


class Doc2X:
    def __init__(
        self,
        apikey: str = None,
        thread: int = 1,
        max_pages: int = 1000,
        retry_time: int = 15,
        max_time: int = 90,
    ) -> None:
        self.apikey = apikey or os.environ.get("DOC2X_APIKEY", "")
        if not self.apikey:
            raise ValueError("No apikey found")
        self.retry_time = retry_time
        self.max_time = max_time
        if thread != 1:
            warnings.warn(
                "The 'thread' parameter is deprecated. Now only the maximum total pages `max_pages` processed simultaneously can be specified.",
                DeprecationWarning,
            )
        self.max_pages = max_pages

    async def pdf2file_back(
        self,
        pdf_file,
        output_names: List[str] = None,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
    ) -> Tuple[List[str], List[dict], bool]:
        if isinstance(pdf_file, str):
            pdf_file, output_names = (
                get_files(path=pdf_file, mode="pdf", out=output_format)
                if os.path.isdir(pdf_file)
                else ([pdf_file], None)
            )

        output_names = output_names or [None] * len(pdf_file)
        if len(pdf_file) != len(output_names):
            raise ValueError("The length of files and output_names should be the same.")

        output_format = (
            OutputFormat(output_format).value
            if isinstance(output_format, OutputFormat)
            else output_format
        )

        semaphore = asyncio.Semaphore(self.max_pages)

        async def process_file(pdf, name):
            try:
                page_count = get_pdf_page_count(pdf)
            except Exception as e:
                logging.warning(f"Failed to get page count for {pdf}: {str(e)}")
                page_count = self.max_pages  #! Assume the worst case

            async def acquire_semaphore():
                for _ in range(page_count):
                    await semaphore.acquire()

            try:
                await acquire_semaphore()
                try:
                    result = await asyncio.wait_for(
                        pdf2file(
                            apikey=self.apikey,
                            pdf_path=pdf,
                            output_path=os.path.join(output_path),
                            output_format=output_format,
                            output_name=name,
                            ocr=ocr,
                            wait_time=15,
                            max_time=self.max_time,
                            maxretry=self.retry_time,
                            convert=convert,
                        ),
                        timeout=self.max_time * 2,
                    )
                    return result, "", True
                except asyncio.TimeoutError:
                    return "", "Operation timed out", False
                except Exception as e:
                    return "", str(e), False
            finally:
                #! Assuming that the semaphore release should be done regardless of the outcome
                for _ in range(page_count):
                    semaphore.release()

        results = await asyncio.gather(
            *[process_file(pdf, name) for pdf, name in zip(pdf_file, output_names)]
        )

        success_files = [r[0] if r[2] else "" for r in results]
        failed_files = [
            {"error": r[1], "path": pdf} if not r[2] else {"error": "", "path": ""}
            for r, pdf in zip(results, pdf_file)
        ]
        has_error = any(not r[2] for r in results)

        if has_error:
            failed_count = sum(1 for fail in failed_files if fail["error"] != "")
            logging.warning(
                f"{failed_count} file(s) failed to convert, please check the log."
            )

        return success_files, failed_files, has_error

    def pdf2file(self, *args, **kwargs):
        return run_async(self.pdf2file_back(*args, **kwargs))
