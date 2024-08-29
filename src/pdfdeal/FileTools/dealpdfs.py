import os
from .file_tools import extract_text_and_images
from .ocr import load_build_in_ocr, BUILD_IN_OCR
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from ..Doc2X.Types import RAG_OutputType
import uuid
from typing import Tuple, Callable
from .file_tools import list_rename
import logging


def strore_pdf(pdf_path, Text):
    c = canvas.Canvas(pdf_path, pagesize=letter)

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    c.setFont("STSong-Light", 12)

    for text in Text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            c.setFont("STSong-Light", 12)
            c.drawString(100, 750 - i * 13, line)
        c.showPage()
    c.save()


def deal_pdf_back(
    input,
    output: RAG_OutputType = RAG_OutputType.PDF,
    ocr=None,
    language: list = ["ch_sim", "en"],
    GPU: bool = False,
    path: str = "./Output",
):
    pdf_path = input

    Text, All_Done = extract_text_and_images(
        pdf_path=pdf_path, ocr=ocr, language=language, GPU=GPU
    )

    if output == "texts":
        return Text, All_Done

    else:
        filename = pdf_path.split("/")[-1].replace(".pdf", f"_{uuid.uuid4()}.{output}")
        os.makedirs(path, exist_ok=True)
        if output == "md":
            try:
                output_md_path = os.path.join(path, filename)
                with open(output_md_path, "w") as file:
                    for text in Text:
                        file.write(text + "\n")
                return output_md_path, All_Done
            except Exception as e:
                RuntimeError(f"Failed to save the markdown file: {e}")
        elif output == "pdf":
            output_pdf_path = os.path.join(path, filename)
            try:
                strore_pdf(output_pdf_path, Text)
                return output_pdf_path, All_Done
            except Exception as e:
                RuntimeError(f"Failed to save the PDF file: {e}")


def deal_pdf(
    pdf_file,
    output_format: str = "pdf",
    output_names: list = None,
    ocr=None,
    language: list = ["ch_sim", "en"],
    GPU: bool = False,
    output_path: str = "./Output",
    option: dict = {},
) -> Tuple[list, list, bool]:
    """Deal with PDF files with OCR, make PDF more readable for RAG

    Args:
        pdf_file (str or list): input file path, str or list
        output_format (str, optional): the type of output, "texts" "md" or "pdf", default is "pdf". Defaults to "pdf".
        output_names (list, optional): Custom Output File Names, must be the same length as `image_file`. Defaults to None.
        ocr (function, optional): custom ocr/tool function, not define will use easyocr. Or use `string`: `pytesseract` to use pytesseract, string `pass` to skip OCR. Defaults to None.
        language (list, optional): the language used in OCR, default is ["ch_sim", "en"] for easyocr, ["eng"] for pytesseract. Defaults to ["ch_sim", "en"].
        GPU (bool, optional): whether to use GPU in OCR, default is False, not working for pytesseract. Defaults to False.
        output_path (str, optional): the path of folder to save the output, default is "./Output", only used when output is "md" or "pdf". Defaults to "./Output".
        option (dict, optional): the option of the OCR/tool. Defaults to `{}`.

    Returns:
        tuple[list,list,str]:
        will return `list1`,`list2`,`bool`
            `list1`: list of successful files path, if some files are failed, its path will be empty string
            `list2`: list of failed files's error message and its original file path, id some files are successful, its error message will be empty string
            `bool`: True means that at least one file process failed
    """
    output_format = RAG_OutputType(output_format)
    if isinstance(output_format, RAG_OutputType):
        output_format = output_format.value

    if isinstance(pdf_file, str):
        if not pdf_file.endswith(".pdf"):
            RuntimeError("The input must be path to a PDF file")
        pdf_file = [pdf_file]

    ocr = ocr or "easyocr"

    if isinstance(ocr, Callable):
        if len(ocr.__code__.co_varnames) == 2:
            # if using tool function
            option["output"] = output_path
            return ocr(pdf_file, option)

    elif isinstance(ocr, str):
        if ocr in BUILD_IN_OCR:
            ocr, _, _ = load_build_in_ocr(ocr)
        else:
            RuntimeError(f"OCR {ocr} is not supported.")
    else:
        raise RuntimeError("The ocr must be a function or a string")

    success_file = []
    failed_file = []
    error_flag = False
    for pdf_path in pdf_file:
        try:
            output, All_Done = deal_pdf_back(
                pdf_path, output_format, ocr, language, GPU, output_path
            )
            success_file.append(output)
            if not All_Done:
                failed_file.append(
                    {
                        "error": "Some pictures are failed to OCR, but the text and reset pictures is extracted",
                        "file": pdf_path,
                    }
                )
            else:
                failed_file.append({"error": "", "file": ""})
        except Exception as e:
            All_Done = True  # * As this flag is use to determine if the OCR is done, we set it to True here
            success_file.append("")
            failed_file.append({"error": str(e), "file": pdf_path})
            error_flag = True
    logging.info(
        f"PDFDEAL Progress: {sum(1 for s in success_file if s != '')}/{len(pdf_file)} files successfully processed."
    )
    if All_Done is False:
        logging.warning(
            "Some pictures are failed to OCR, but the text and reset pictures is extracted"
        )
    if error_flag:
        for f in failed_file:
            if f["error"] != "":
                logging.error(
                    f"-----\nFailed to process file: {f['file']} with error: {f['error']}\n-----"
                )

    if output_names is not None:
        success_file = list_rename(success_file, output_names)

    return success_file, failed_file, error_flag
