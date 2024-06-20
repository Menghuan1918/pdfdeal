import asyncio
from aiolimiter import AsyncLimiter
import os
from .Doc2X.Exception import RateLimit
from .get_file import strore_pdf
from typing import Tuple

from .Doc2X.Convert import (
    refresh_key,
    get_limit,
    uuid2file,
    upload_pdf,
    upload_img,
    uuid_status,
    check_folder,
)


async def get_key(apikey: str) -> str:
    """
    Get apikey from environment variable or input
    """
    if apikey is None:
        apikey = os.environ.get("DOC2X_APIKEY", "")
    if apikey == "":
        raise ValueError("No apikey found")
    if not apikey.startswith("sk-"):
        apikey = await refresh_key(apikey)
    return apikey


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
):
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
            print(f"Reach the rate limit, wait for {60 // rpm + 15} seconds")
            await asyncio.sleep(60 // rpm + 15)
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
        # If translate is True, return texts and other(texts location inside)
        elif status_process == 100 and status_str == "Translate success":
            final = {"texts": texts, "location": other}
            return final
        print(f"{status_str}: {status_process}%    -- uuid: {uuid}")
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
            print(f"Reach the rate limit, wait for {60 // rpm + 15} seconds")
            await asyncio.sleep(60 // rpm + 15)
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
        print(f"{status_str}: {status_process}%    -- uuid: {uuid}")
        await asyncio.sleep(1)
    return await uuid2file(
        apikey=apikey, uuid=uuid, output_path=output_path, output_format=output_format
    )


class Doc2X:
    """
    `apikey`: Your apikey, or get from environment variable `DOC2X_APIKEY`
    `rpm`: Request per minute, default is `3`
    `thread`: Max thread number, default is `1`
    `maxretry`: Max retry times, default is `5`
    """

    def __init__(
        self, apikey: str = None, rpm: int = 3, thread: int = 1, maxretry: int = 5
    ) -> None:
        self.apikey = asyncio.run(get_key(apikey))
        self.limiter = AsyncLimiter(max_rate=rpm - 1, time_period=60)
        time_period = int(60 // rpm)
        self.concurrency = AsyncLimiter(max_rate=thread, time_period=time_period)
        self.rpm = rpm
        self.thread = thread
        self.maxretry = maxretry

    async def pic2file_back(
        self,
        image_file: list,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        img_correction: bool = True,
        equation=False,
        convert: bool = False,
    ) -> str:
        """
        Convert image file to specified file, with rate/thread limit
        input refers to `pic2file` function
        """
        total = len(image_file)

        async def limited_img2file_v1(img):
            async with self.concurrency:
                async with self.limiter:
                    return await img2file_v1(
                        apikey=self.apikey,
                        img_path=img,
                        output_path=output_path,
                        output_format=output_format,
                        formula=equation,
                        img_correction=img_correction,
                        maxretry=self.maxretry,
                        rpm=self.rpm,
                        convert=convert,
                    )

        task = [limited_img2file_v1(img) for img in image_file]
        completed_tasks = await asyncio.gather(*task)
        for i, _ in enumerate(completed_tasks):
            print(f"PICTURE Progress: {i + 1}/{total} files processed.")
        return completed_tasks

    def pic2file(
        self,
        image_file,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        img_correction: bool = True,
        equation=False,
        convert: bool = False,
    ) -> str:
        """
        Convert image file to specified file
        `image_file`: image file path or a list of image file path
        `output_path`: output folder path, default is "./Output"
        `output_format`: output format, accept `texts`, `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`
        `img_correction`: whether to correct the image, default is `True`
        `equation`: whether the image is an equation, default is `False`
        `convert`: whether to convert `[` to `$` and `[[` to `$$`, default is False

        return: output file path
        """
        if isinstance(image_file, str):
            image_file = [image_file]
            return asyncio.run(
                self.pic2file_back(
                    image_file,
                    output_path,
                    output_format,
                    img_correction,
                    equation,
                    convert,
                )
            )[0]
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
        pdf_file: list,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
        translate: bool = False,
    ) -> str:
        """
        Convert pdf file to specified file, with rate/thread limit, async version
        input refers to `pdf2file` function
        """
        total = len(pdf_file)

        async def limited_pdf2file_v1(pdf):
            async with self.concurrency:
                async with self.limiter:
                    return await pdf2file_v1(
                        apikey=self.apikey,
                        pdf_path=pdf,
                        output_path=output_path,
                        output_format=output_format,
                        ocr=ocr,
                        maxretry=self.maxretry,
                        rpm=self.rpm,
                        convert=convert,
                        translate=translate,
                    )

        tasks = [limited_pdf2file_v1(pdf) for pdf in pdf_file]
        completed_tasks = await asyncio.gather(*tasks)
        for i, _ in enumerate(completed_tasks):
            print(f"PDF Progress: {i + 1}/{total} files processed.")
        return completed_tasks

    def pdf2file(
        self,
        pdf_file,
        output_path: str = "./Output",
        output_format: str = "md_dollar",
        ocr: bool = True,
        convert: bool = False,
    ) -> str:
        """
        Convert pdf file to specified file
        `pdf_file`: pdf file path, or a list of pdf file path
        `output_path`: output folder path, default is "./Output"
        `output_format`: output format, accept `texts`, `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`
        `ocr`: whether to use OCR, default is True
        `convert`: whether to convert `[` to `$` and `[[` to `$$`, default is False

        return: output file path
        """
        if isinstance(pdf_file, str):
            input = [pdf_file]
            return asyncio.run(
                self.pdf2file_back(
                    input, output_path, output_format, ocr, convert, False
                )
            )[0]
        return asyncio.run(
            self.pdf2file_back(
                pdf_file, output_path, output_format, ocr, convert, False
            )
        )

    def get_limit(self) -> int:
        """
        Get the limit of the apikey
        """
        return asyncio.run(get_limit(self.apikey))

    async def pdfdeal_back(
        self,
        input: str,
        output: str,
        path: str,
        convert: bool,
    ) -> str:
        """
        Convert pdf files into recognisable pdfs, significantly improving their effectiveness in RAG systems
        async version function
        """
        async with self.concurrency:
            async with self.limiter:
                texts = await pdf2file_v1(
                    apikey=self.apikey,
                    pdf_path=input,
                    output_path=output,
                    output_format="texts",
                    ocr=True,
                    maxretry=self.maxretry,
                    rpm=self.rpm,
                    convert=convert,
                    translate=False,
                )
                await check_folder(path)
                file_name = os.path.basename(input).replace(".pdf", f".{output}")
                output_path = os.path.join(path, file_name)
                if output == "pdf":
                    strore_pdf(output_path, texts)
                else:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(texts)
                return output_path

    async def pdfdeals(
        self,
        pdf_files: list,
        output_path: str = "./Output",
        output_format: str = "pdf",
        convert: bool = True,
    ) -> list:
        """
        Convert pdf files into recognisable pdfs, significantly improving their effectiveness in RAG systems
        async version function, input refers to `pdfdeal` function
        """
        total = len(pdf_files)
        tasks = [
            self.pdfdeal_back(pdf_file, output_format, output_path, convert)
            for pdf_file in pdf_files
        ]
        completed_tasks = await asyncio.gather(*tasks)
        for i, _ in enumerate(completed_tasks):
            print(f"PDFDEAL Progress: {i + 1}/{total} files processed.")
        return completed_tasks

    def pdfdeal(
        self,
        input,
        output: str = "pdf",
        path: str = "./Output",
        convert: bool = True,
    ) -> str:
        """
        `input`: input file path
        `output`: output format, default is 'pdf', accept 'pdf', 'md'
        `path`: output path, default is './Output'
        `convert`: whether to convert "[" to "$" and "[[" to "$$", default is True
        """
        if isinstance(input, str):
            input = [input]
            return asyncio.run(self.pdfdeals(input, path, output, convert))[0]
        return asyncio.run(self.pdfdeals(input, path, output, convert))

    def pdf_translate(
        self,
        pdf_file,
        output_path: str = "./Output",
        convert: bool = False,
    ) -> Tuple[list, list]:
        """
        Translate pdf file to specified file
        `pdf_file`: pdf file path, or a list of pdf file path
        `output_path`: output folder path, default is "./Output"
        `ocr`: whether to use OCR, default is True
        `convert`: whether to convert "[" to "$" and "[[" to "$$", default is False

        return: list of translated texts and list of translated texts location
        """
        if isinstance(pdf_file, str):
            pdf_file = [pdf_file]
            return asyncio.run(
                self.pdf2file_back(pdf_file, output_path, "texts", True, convert, True)
            )
        return asyncio.run(
            self.pdf2file_back(pdf_file, output_path, "texts", True, convert, True)
        )


def Doc2x(api_key):
    """
    Deprecated function, use `from pdfdeal.doc2x import Doc2X` instead
    """
    from .doc2x_old import Doc2x
    import warnings

    warnings.warn(
        "This function is deprecated, please use `from pdfdeal.doc2x import Doc2X` instead"
    )
    return Doc2x(api_key)
