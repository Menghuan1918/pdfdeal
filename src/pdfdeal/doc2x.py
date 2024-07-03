import asyncio
import os
from .Doc2X.Exception import RateLimit, RateLimiter
from .Doc2X.Types import OutputFormat, OutputVersion, RAG_OutputType
from .FileTools.dealpdfs import strore_pdf
from typing import Tuple
from .FileTools.file_tools import list_rename

from .Doc2X.Convert import (
    refresh_key,
    get_limit,
    uuid2file,
    upload_pdf,
    upload_img,
    uuid_status,
    check_folder,
    process_status,
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
        while True:
            print(f"Reach the rate limit, wait for {60 // rpm + 15} seconds")
            await asyncio.sleep(60 // rpm + 15)
            try:
                uuid = await upload_pdf(apikey=apikey, pdffile=pdf_path, ocr=ocr)
                break
            except RateLimit:
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
            print(f"{status_str}: {status_process}%    -- uuid: {uuid}")
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
        while True:
            print(f"Reach the rate limit, wait for {60 // rpm + 15} seconds")
            await asyncio.sleep(60 // rpm + 15)
            try:
                uuid = await upload_img(
                    apikey=apikey,
                    imgfile=img_path,
                    formula=formula,
                    img_correction=img_correction,
                )
                break
            except RateLimit:
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
            print(f"{status_str}: {status_process}%    -- uuid: {uuid}")
            break
        print(f"{status_str}: {status_process}%    -- uuid: {uuid}")
        await asyncio.sleep(1)
    return await uuid2file(
        apikey=apikey, uuid=uuid, output_path=output_path, output_format=output_format
    )


class Doc2X:
    """
    `apikey`: Your apikey, or get from environment variable `DOC2X_APIKEY`
    `rpm`: Request per minute, will automatically adjust the rate limit according to the apikey
    `thread`: deprecated
    `maxretry`: deprecated
    """

    def __init__(
        self,
        apikey: str = None,
        rpm: int = None,
        thread: int = None,
        maxretry: int = None,
    ) -> None:
        self.apikey = asyncio.run(get_key(apikey))
        if rpm is not None:
            self.rpm = rpm
        else:
            if self.apikey.startswith("sk-"):
                self.rpm = 10
            else:
                self.rpm = 4
        self.limiter = RateLimiter(self.rpm)
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
        limit = asyncio.Semaphore(self.rpm)
        lock = asyncio.Lock()

        async def limited_img2file_v1(img):
            try:
                await limit.acquire()
                await self.limiter.require(lock)
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
            except Exception as e:
                return f"Error {e}"
            finally:
                limit.release()

        task = [limited_img2file_v1(img) for img in image_file]
        completed_tasks = await asyncio.gather(*task)
        return await process_status(image_file, completed_tasks)

    def pic2file(
        self,
        image_file,
        output_path: str = "./Output",
        output_names: list = None,
        output_format: OutputFormat = OutputFormat.MD_DOLLAR,
        img_correction: bool = True,
        equation: bool = False,
        convert: bool = False,
        version: OutputVersion = OutputVersion.V1,
    ):
        """
        Convert image file to specified file

        Args:
            `image_file`: image file path or a list of image file path
            `output_path`: output folder path, default is "./Output"
            `output_format`: output format, accept `texts`, `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`
            `img_correction`: whether to correct the image, default is `True`
            `equation`: whether the image is an equation, default is `False`
            `convert`: whether to convert `[` to `$` and `[[` to `$$`, default is False
            `version`: If version is `v2`, will return more information, default is `v1`

        Return:
            `list`: output file path

            if `version` is set to `v2`, will return `list1`,`list2`,`bool`
                `list1`: list of successful files path, if some files are failed, its path will be empty string
                `list2`: list of failed files's error message and its original file path, id some files are successful, its error message will be empty string
                `bool`: True means that at least one file process failed
        """
        output_format = OutputFormat(output_format)
        if isinstance(output_format, OutputFormat):
            output_format = output_format.value
        version = OutputVersion(version)
        if isinstance(version, OutputVersion):
            version = version.value

        if isinstance(image_file, str):
            image_file = [image_file]

        if output_names is not None:
            if len(image_file) != len(output_names):
                raise ValueError(
                    "The length of files and output_names should be the same."
                )

        success, failed, flag = asyncio.run(
            self.pic2file_back(
                image_file,
                output_path,
                output_format,
                img_correction,
                equation,
                convert,
            )
        )

        print(
            f"IMG Progress: {sum(1 for s in success if s != '')}/{len(image_file)} files successfully processed."
        )
        if flag:
            for failed_file in failed:
                if failed_file["error"] != "":
                    print(
                        f"-----\nFailed deal with {failed_file['path']} with error:\n{failed_file['error']}\n-----"
                    )

        if output_names is not None:
            success = list_rename(success, output_names)

        if version == "v2":
            return success, failed, flag
        return success

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
        limit = asyncio.Semaphore(self.rpm)
        lock = asyncio.Lock()

        async def limited_pdf2file_v1(pdf):
            try:
                await limit.acquire()
                await self.limiter.require(lock)
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
            except Exception as e:
                return f"Error {e}"
            finally:
                limit.release()

        tasks = [limited_pdf2file_v1(pdf) for pdf in pdf_file]
        completed_tasks = await asyncio.gather(*tasks)
        return await process_status(pdf_file, completed_tasks)

    def pdf2file(
        self,
        pdf_file,
        output_path: str = "./Output",
        output_names: list = None,
        output_format: OutputFormat = OutputFormat.MD_DOLLAR,
        ocr: bool = True,
        convert: bool = False,
        version: str = OutputVersion.V1,
    ):
        """
        Convert pdf file to specified file

        Args:
            `pdf_file`: pdf file path, or a list of pdf file path
            `output_path`: output folder path, default is "./Output"
            `output_names`: Custom Output File Names, must be the same length as `pdf_file`, default is `None`(file name will be its uuid)
            `output_format`: output format, accept `texts`, `md`, `md_dollar`, `latex`, `docx`, deafult is `md_dollar`
            `ocr`: whether to use OCR, default is True
            `convert`: whether to convert `[` to `$` and `[[` to `$$`, default is False
            `version`: If version is `v2`, will return more information, default is `v1`

        Return:
            `list`: output file path

            if `version` is set to `v2`, will return `list1`,`list2`,`bool`
                `list1`: list of successful files path, if some files are failed, its path will be empty string
                `list2`: list of failed files's error message and its original file path, id some files are successful, its error message will be empty string
                `bool`: True means that at least one file process failed
        """
        output_format = OutputFormat(output_format)
        if isinstance(output_format, OutputFormat):
            output_format = output_format.value
        version = OutputVersion(version)
        if isinstance(version, OutputVersion):
            version = version.value

        if isinstance(pdf_file, str):
            pdf_file = [pdf_file]

        if output_names is not None:
            if len(pdf_file) != len(output_names):
                raise ValueError(
                    "The length of files and output_names should be the same."
                )

        success, failed, flag = asyncio.run(
            self.pdf2file_back(
                pdf_file, output_path, output_format, ocr, convert, False
            )
        )
        print(
            f"PDF Progress: {sum(1 for s in success if s != '')}/{len(pdf_file)} files successfully processed."
        )
        if flag:
            for failed_file in failed:
                if failed_file["error"] != "":
                    print(
                        f"-----\nFailed deal with {failed_file['path']} with error:\n{failed_file['error']}\n-----"
                    )

        if output_names is not None:
            success = list_rename(success, output_names)

        if version == "v2":
            return success, failed, flag
        return success

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
    ):
        """
        Convert pdf files into recognisable pdfs, significantly improving their effectiveness in RAG systems
        async version function
        """
        limit = asyncio.Semaphore(self.rpm)
        lock = asyncio.Lock()
        try:
            await limit.acquire()
            await self.limiter.require(lock)
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
            elif output == "texts":
                return texts, "", True
            else:
                md_text = '\n'.join(texts) + '\n'
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
            return output_path, "", True
        except Exception as e:
            return input, e, False
        finally:
            limit.release()

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
        tasks = [
            self.pdfdeal_back(pdf_file, output_format, output_path, convert)
            for pdf_file in pdf_files
        ]
        completed_tasks = await asyncio.gather(*tasks)
        success_file = []
        error_file = []
        error_flag = False
        for temp in completed_tasks:
            path = temp[0]
            error = temp[1]
            flag = temp[2]
            if flag:
                success_file.append(path)
                error_file.append({"error": "", "path": ""})
            else:
                success_file.append("")
                error_file.append({"error": error, "path": path})
                error_flag = True
        return success_file, error_file, error_flag

    def pdfdeal(
        self,
        input,
        output: str = RAG_OutputType.PDF,
        path: str = "./Output",
        convert: bool = True,
        version: str = OutputVersion.V1,
    ):
        """
        Deal with pdf file, convert it to specified format for RAG system

        Args:
            `input`: input file path
            `output`: output format, default is 'pdf', accept 'pdf', 'md' or 'texts'
            `path`: output path, default is './Output'
            `convert`: whether to convert "[" to "$" and "[[" to "$$", default is True
            `version`: If version is `v2`, will return more information, default is `v1`

        Return:
            `list`: output file path

            if `version` is set to `v2`, will return `list1`,`list2`,`bool`
                `list1`: list of successful files path, if some files are failed, its path will be empty string
                `list2`: list of failed files's error message and its original file path, id some files are successful, its error message will be empty string
                `bool`: True means that at least one file process failed
        """
        output = RAG_OutputType(output)
        if isinstance(output, RAG_OutputType):
            output = output.value
        version = OutputVersion(version)
        if isinstance(version, OutputVersion):
            version = version.value

        if isinstance(input, str):
            input = [input]

        success, failed, flag = asyncio.run(self.pdfdeals(input, path, output, convert))
        print(
            f"PDFDEAL Progress: {sum(1 for s in success if s != '')}/{len(input)} files successfully processed."
        )
        if flag:
            for failed_file in failed:
                if failed_file["error"] != "":
                    print(
                        f"-----\nFailed deal with {failed_file['path']} with error:\n{failed_file['error']}\n-----"
                    )
        if version == "v2":
            return success, failed, flag
        return success

    def pdf_translate(
        self,
        pdf_file,
        output_path: str = "./Output",
        convert: bool = False,
        version: str = OutputVersion.V1,
    ) -> Tuple[list, list]:
        """
        Translate pdf file to specified file

        Args:
            `pdf_file`: pdf file path, or a list of pdf file path
            `output_path`: output folder path, default is "./Output"
            `ocr`: whether to use OCR, default is True
            `convert`: whether to convert "[" to "$" and "[[" to "$$", default is False
            `version`: If version is `v2`, will return more information, default is `v1`

        return:
            `list`: list of translated texts and list of translated texts location

            if `version` is set to `v2`, will return `list1`,`list2`,`bool`
                `list1`: list of translated texts and list of translated texts location, if some files are failed, its place will be empty string
                `list2`: list of failed files's error message and its original file path, id some files are successful, its error message will be empty string
                `bool`: True means that at least one file process failed
        """
        version = OutputVersion(version)
        if isinstance(version, OutputVersion):
            version = version.value
        if self.apikey.startswith("sk-"):
            raise RuntimeError(
                "Your secret key does not have access to the translation function! Please use your personal key."
            )
        if isinstance(pdf_file, str):
            pdf_file = [pdf_file]
        success, failed, flag = asyncio.run(
            self.pdf2file_back(pdf_file, output_path, "texts", True, convert, True)
        )
        print(
            f"TRANSLATE Progress: {sum(1 for s in success if s != '')}/{len(pdf_file)} files successfully processed."
        )
        if flag:
            for failed_file in failed:
                if failed_file["error"] != "":
                    print(
                        f"-----\nFailed deal with {failed_file['path']} with error:\n{failed_file['error']}\n-----"
                    )
        if version == "v2":
            return success, failed, flag
        return success


def Doc2x(api_key):
    """
    Deprecated function, use `from pdfdeal.doc2x import Doc2X` instead
    """
    raise DeprecationWarning(
        "Deprecated function, use `from pdfdeal.doc2x import Doc2X` instead, please visit https://github.com/Menghuan1918/pdfdeal/blob/main/docs/doc2x.md for more information."
    )
