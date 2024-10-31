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
import time

logger = logging.getLogger(name="pdfdeal.doc2x")


async def parse_pdf(
    apikey: str,
    pdf_path: str,
    ocr: bool,
    maxretry: int,
    wait_time: int,
    max_time: int,
    convert: bool,
    oss_choose: str = "auto",
) -> Tuple[str, List[str], List[dict]]:
    """Parse PDF file and return uid and extracted text"""

    async def task_limit_lock():
        global full_speed
        if full_speed:
            global limit_lock, get_max_limit, max_threads, thread_min
            nonlocal thread_lock
            if not get_max_limit and not thread_lock:
                get_max_limit = True
                thread_lock = True
                async with limit_lock:
                    max_threads = max(thread_min, max_threads - 1)
            else:
                if not thread_lock:
                    async with limit_lock:
                        max_threads = max(thread_min, max_threads - 1)
                    thread_lock = True

    thread_lock = False
    for attempt in range(maxretry):
        try:
            logger.info(f"Uploading {pdf_path}...")
            uid = await upload_pdf(apikey, pdf_path, ocr, oss_choose)
            logger.info(f"Uploading successful for {pdf_path} with uid {uid}")

            for _ in range(max_time // 3):
                try:
                    progress, status, texts, locations = await uid_status(
                        apikey, uid, convert
                    )
                    if status == "Success":
                        logger.info(f"Parsing successful for {pdf_path} with uid {uid}")
                        return uid, texts, locations
                    elif status == "Processing file":
                        logger.info(f"Processing {uid} : {progress}%")
                        await asyncio.sleep(3)
                    else:
                        raise RequestError(
                            f"Unexpected status: {status} with uid: {uid}"
                        )
                except RateLimit:
                    logger.warning(
                        "Rate limit reached during status check, retrying from upload..."
                    )
                    await task_limit_lock()
                    await asyncio.sleep(wait_time)
                    break
            else:
                raise RequestError(f"Max time reached for uid_status with uid: {uid}")
        except RateLimit:
            if attempt < maxretry - 1:
                await task_limit_lock()
                logger.warning("Rate limit reached during upload, retrying...")
                await asyncio.sleep(wait_time)
            else:
                raise RequestError(
                    "Max retry reached for parse_pdf, this may be a rate limit issue, try to reduce the number of threads."
                )

    raise RequestError("Failed to parse PDF after maximum retries")


async def convert_to_format(
    apikey: str,
    uid: str,
    output_format: str,
    output_path: str,
    output_name: str,
    max_time: int,
) -> str:
    """Convert parsed PDF to specified format"""

    logger.info(f"Converting {uid} to {output_format}...")
    status, url = await convert_parse(apikey, uid, output_format)

    for _ in range(max_time // 3):
        if status == "Success":
            logger.info(f"Downloading {uid} {output_format} file to {output_path}...")
            return await download_file(
                url=url,
                file_type=output_format,
                target_folder=output_path,
                target_filename=output_name or uid,
            )
        elif status == "Processing":
            logger.info(f"Converting {uid} {output_format} file...")
            await asyncio.sleep(3)
            status, url = await get_convert_result(apikey, uid)
        else:
            raise RequestError(f"Unexpected status: {status} with uid: {uid}")
    raise RequestError(f"Max time reached for get_convert_result with uid: {uid}")


class Doc2X:
    def __init__(
        self,
        apikey: str = None,
        thread: int = 5,
        max_pages: int = 1000,
        retry_time: int = 5,
        max_time: int = 90,
        debug: bool = False,
        full_speed: bool = False,
    ) -> None:
        """
        Initialize a Doc2X client.

        Args:
            apikey (str, optional): The API key for Doc2X. If not provided, it will try to get from environment variable 'DOC2X_APIKEY'.
            thread (int, optional): The maximum number of concurrent threads at same time. Defaults to 5.
            max_pages (int, optional): The maximum number of pages to process at same time. Defaults to 1000.
            retry_time (int, optional): The number of retry attempts. Defaults to 5.
            max_time (int, optional): The maximum time (in seconds) to wait for a response. Defaults to 90.
            debug (bool, optional): Whether to enable debug logging. Defaults to False.
            full_speed (bool, optional): **Experimental function**. Whether to enable automatic sniffing of the concurrency limit. Defaults to False.

        Raises:
            ValueError: If no API key is found.

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
        self.request_interval = 0.1
        self.full_speed = full_speed

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
        oss_choose: str = "auto",
    ) -> Tuple[List[str], List[dict], bool]:
        if isinstance(pdf_file, str):
            if os.path.isdir(pdf_file):
                pdf_file, output_names = get_files(
                    path=pdf_file, mode="pdf", out=output_format
                )
            else:
                pdf_file = [pdf_file]
                if output_names is None:
                    output_names = [os.path.basename(pdf_file[0])]

        output_names = output_names or [None] * len(pdf_file)
        if len(pdf_file) != len(output_names):
            raise ValueError("The length of files and output_names should be the same.")

        try:
            output_format = OutputFormat(output_format)
        except ValueError as e:
            raise ValueError(f"Invalid output format: {e}")

        output_format = output_format.value

        # Track total pages and last request time
        total_pages = 0
        last_request_time = 0
        page_lock = asyncio.Lock()
        parse_tasks = set()
        convert_tasks = set()
        results = [None] * len(pdf_file)
        parse_results = [None] * len(pdf_file)
        global limit_lock, get_max_limit, max_threads, full_speed, thread_min
        thread_min = self.thread
        full_speed = self.full_speed
        limit_lock = asyncio.Lock()
        get_max_limit = False
        max_threads = self.thread

        if full_speed:
            self.max_time = 180
            self.retry_time = 10
            self.request_interval = 0.01

        async def process_file(index, pdf, name):
            try:
                page_count = get_pdf_page_count(pdf)
            except RequestError as e:
                results[index] = ("", str(e), False)
                logger.warning(f"Failed to get page count for {pdf}: {str(e)}")
                return
            except Exception as e:
                logger.warning(f"Failed to get page count for {pdf}: {str(e)}")
                page_count = self.max_pages - 1  #! Assume the worst case
            if page_count > self.max_pages:
                logger.warning(f"File {pdf} has too many pages, skipping.")
                results[index] = ("", "File has too many pages", False)
                return

            nonlocal total_pages, last_request_time

            try:
                # Check if we can start new task
                while True:
                    async with page_lock:
                        if total_pages + page_count <= self.max_pages:
                            current_time = time.time()
                            if current_time - last_request_time < self.request_interval:
                                await asyncio.sleep(
                                    self.request_interval
                                    - (current_time - last_request_time)
                                )

                            total_pages += page_count
                            last_request_time = time.time()
                            break
                    await asyncio.sleep(0.1)

                # Process the file
                try:
                    uid, texts, locations = await parse_pdf(
                        apikey=self.apikey,
                        pdf_path=pdf,
                        ocr=ocr,
                        maxretry=self.retry_time,
                        wait_time=5,
                        max_time=self.max_time,
                        convert=convert,
                        oss_choose=oss_choose,
                    )
                    parse_results[index] = (uid, texts, locations)
                    # Create convert task as soon as parse is complete
                    task = asyncio.create_task(convert_file(index, name))
                    convert_tasks.add(task)

                except asyncio.TimeoutError:
                    results[index] = (
                        "",
                        "Operation timed out, this may be a rate limit issue or network issue, try to reduce the number of threads.",
                        False,
                    )
                except Exception as e:
                    results[index] = ("", str(e), False)
            finally:
                async with page_lock:
                    total_pages -= page_count

        async def convert_file(index, name):
            if parse_results[index] is None:
                return

            uid, texts, locations = parse_results[index]
            try:
                if output_format in ["md", "md_dollar", "tex", "docx"]:
                    nonlocal last_request_time
                    # Wait for request interval
                    current_time = time.time()
                    if current_time - last_request_time < self.request_interval:
                        await asyncio.sleep(
                            self.request_interval - (current_time - last_request_time)
                        )

                    async with page_lock:
                        last_request_time = time.time()

                    result = await convert_to_format(
                        apikey=self.apikey,
                        uid=uid,
                        output_format=output_format,
                        output_path=output_path,
                        output_name=name,
                        max_time=self.max_time,
                    )
                else:
                    if output_format == "texts":
                        result = texts
                    elif output_format == "text":
                        result = "\n".join(texts)
                    elif output_format == "detailed":
                        result = [
                            {"text": text, "location": loc}
                            for text, loc in zip(texts, locations)
                        ]
                    else:
                        raise ValueError(f"Unsupported output format: {output_format}")

                results[index] = (result, "", True)
            except asyncio.TimeoutError:
                results[index] = (
                    "",
                    "Operation timed out, this may be a rate limit issue or network issue, try to reduce the number of threads.",
                    False,
                )
            except Exception as e:
                results[index] = ("", str(e), False)

        # Create and run parse tasks with controlled concurrency
        for i, (pdf, name) in enumerate(zip(pdf_file, output_names)):
            while len(parse_tasks) >= max_threads:
                done, parse_tasks = await asyncio.wait(
                    parse_tasks, return_when=asyncio.FIRST_COMPLETED
                )
                if full_speed:
                    async with limit_lock:
                        if not get_max_limit:
                            max_threads = max_threads + 1
            task = asyncio.create_task(process_file(i, pdf, name))
            parse_tasks.add(task)

        # Wait for remaining parse tasks
        if parse_tasks:
            await asyncio.wait(parse_tasks)

        # Wait for remaining convert tasks
        if convert_tasks:
            await asyncio.wait(convert_tasks)
        else:
            logger.warning("No successful parse tasks, skipping conversion.")

        if full_speed:
            logger.info(f"Convert tasks done with {max_threads} threads.")
        success_files = [r[0] if r and r[2] else "" for r in results]
        failed_files = [
            {"error": r[1] if r else "Unknown error", "path": pdf}
            if not (r and r[2])
            else {"error": "", "path": ""}
            for r, pdf in zip(results, pdf_file)
        ]
        has_error = any(not (r and r[2]) for r in results)

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
                        print("====================================")
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
            output_format (str, optional): Desired output format. Defaults to `md_dollar`. Supported formats include:`md_dollar`|`md`|`tex`|`docx`, will return the path of files, support output variable: `text`|`texts`|`detailed`(it means `string in md format`, `list of strings split by page`, `list of strings split by page (including detailed page information)`)
            ocr (bool, optional): Whether to use OCR. Defaults to True.
            convert (bool, optional): Whether to convert "[" and "[[" to "$" and "$$", only valid if `output_format` is a variable format(`txt`|`txts`|`detailed`). Defaults to False.

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
        oss_choose = "never"  #! DO NOT CHANGE THIS, not finished yet
        return run_async(
            self.pdf2file_back(
                pdf_file=pdf_file,
                output_names=output_names,
                output_path=output_path,
                output_format=output_format,
                ocr=ocr,
                convert=convert,
                oss_choose=oss_choose,
            )
        )
