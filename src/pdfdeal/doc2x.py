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

logger = logging.getLogger(name="pdfdeal.doc2x")


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
                logger.warning("Rate limit reached, retrying...")
                await asyncio.sleep(wait_time)
        raise RequestError("Max retry reached for upload_pdf")

    logger.info(f"Uploading {pdf_path}...")
    try:
        uid = await upload_pdf(apikey, pdf_path, ocr)
    except RateLimit:
        uid = await retry_upload()

    for _ in range(max_time):
        progress, status, texts, locations = await uid_status(apikey, uid, convert)
        if status == "Success":
            logger.info(f"Conversion successful for {pdf_path} with uid {uid}")
            if output_format == "texts":
                return texts
            elif output_format == "text":
                return "\n".join(texts)
            elif output_format == "detailed":
                return [
                    {"text": text, "location": loc}
                    for text, loc in zip(texts, locations)
                ]
            elif output_format in ["md", "md_dollar", "tex", "docx"]:
                logger.info(f"Parsing {uid} to {output_format}...")
                status, url = await convert_parse(apikey, uid, output_format)
                for _ in range(max_time):
                    if status == "Success":
                        logger.info(
                            f"Downloading {uid} {output_format} file to {output_path}..."
                        )
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
            logger.info(f"Processing {uid} : {progress}%")
            await asyncio.sleep(1)
        else:
            raise RequestError(f"Unexpected status: {status}")
    raise RequestError("Max time reached for uid_status")


class Doc2X:
    def __init__(
        self,
        apikey: str = None,
        thread: int = 5,
        max_pages: int = 1000,
        retry_time: int = 15,
        max_time: int = 90,
        debug: bool = False,
    ) -> None:
        """
        Initialize a Doc2X client.

        Args:
            apikey (str, optional): The API key for Doc2X. If not provided, it will try to get from environment variable 'DOC2X_APIKEY'.
            thread (int, optional): The maximum number of concurrent threads. Defaults to 5.
            max_pages (int, optional): The maximum number of pages to process. Defaults to 1000.
            retry_time (int, optional): The number of retry attempts. Defaults to 15.
            max_time (int, optional): The maximum time (in seconds) to wait for a response. Defaults to 90.
            debug (bool, optional): Whether to enable debug logging. Defaults to False.

        Raises:
            ValueError: If no API key is found.

        Attributes:
            apikey (str): The API key for Doc2X.
            retry_time (int): The number of retry attempts.
            max_time (int): The maximum time to wait for a response.
            thread (int): The maximum number of concurrent threads.
            max_pages (int): The maximum number of pages to process.
            debug (bool): Whether debug logging is enabled.

        Note:
            If debug is set to True, it will set the logging level of 'pdfdeal' logger to DEBUG.
        """
        self.apikey = apikey or os.environ.get("DOC2X_APIKEY", "")
        if not self.apikey:
            raise ValueError("No apikey found")
        self.retry_time = retry_time
        self.max_time = max_time
        self.thread = thread
        self.max_pages = max_pages

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False
        if debug:
            logging.getLogger("pdfdeal").setLevel(logging.DEBUG)
        self.debug = debug

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
        thread_semaphore = asyncio.Semaphore(self.thread)

        async def process_file(pdf, name):
            async with thread_semaphore:
                try:
                    page_count = get_pdf_page_count(pdf)
                except Exception as e:
                    logger.warning(f"Failed to get page count for {pdf}: {str(e)}")
                    page_count = self.max_pages  #! Assume the worst case
                if page_count > self.max_pages:
                    logger.warning(f"File {pdf} has too many pages, skipping.")
                    raise ValueError(f"File {pdf} has too many pages.")

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
            logger.error(
                f"{failed_count} file(s) failed to convert, please enable DEBUG mod to check or read the output variable."
            )
            if self.debug:
                for fail in failed_files:
                    if fail["error"] != "":
                        print("====================================")
                        print(f"Failed to convert {fail['path']}: {fail['error']}")
        logger.info(
            f"Successfully converted {sum(1 for file in success_files if file)} file(s)."
        )
        return success_files, failed_files, has_error

    def pdf2file(
        self,
        pdf_file,
        output_names: List[str] = None,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
    ) -> Tuple[List[str], List[dict], bool]:
        """Convert PDF files to the specified format.

        Args:
            pdf_file (str | List[str]): Path to a single PDF file or a list of PDF file paths.
            output_names (List[str], optional): List of output file names. Defaults to None.
            output_path (str, optional): Directory path for output files. Defaults to "./Output".
            output_format (str, optional): Desired output format. Defaults to `md_dollar`. Supported formats include:`md_dollar`|`md`|`tex`|`docx`, support output variable: `txt`|`txts`|`detailed`

            ocr (bool, optional): Whether to use OCR. Defaults to True.
            convert (bool, optional): Whether to convert the PDF. If False, only performs OCR. Defaults to False.

        Returns:
            Tuple[List[str], List[dict], bool]: A tuple containing:

                1. A list of successfully converted file paths or content.
                2. A list of dictionaries containing error information for failed conversions.
                3. A boolean indicating whether any errors occurred during the conversion process.

        Raises:
            Any exceptions raised by pdf2file_back or run_async.

        Note:
            This method provides a convenient synchronous interface for the asynchronous
            PDF conversion functionality. It handles all the necessary setup for running
            the asynchronous code in a synchronous context.
        """
        return run_async(
            self.pdf2file_back(
                pdf_file=pdf_file,
                output_names=output_names,
                output_path=output_path,
                output_format=output_format,
                ocr=ocr,
                convert=convert,
            )
        )
