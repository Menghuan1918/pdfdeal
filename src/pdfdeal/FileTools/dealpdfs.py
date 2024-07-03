import os
from .file_tools import extract_text_and_images
from .ocr import OCR_easyocr, OCR_pytesseract, OCR_pass
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from ..Doc2X.Types import RAG_OutputType, OutputVersion


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
    version: OutputVersion = OutputVersion.V1,
):
    pdf_path = input
    if ocr is None:
        Text, All_Done = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_easyocr, language=language, GPU=GPU
        )
    elif ocr == "pytesseract":
        Text, All_Done = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_pytesseract, language=language, GPU=GPU
        )
    elif ocr == "pass":
        Text, All_Done = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_pass, language=language, GPU=GPU
        )
    else:
        Text, All_Done = extract_text_and_images(
            pdf_path=pdf_path, ocr=ocr, language=language, GPU=GPU
        )
    if output == "texts":
        return Text, All_Done
    else:
        filename = pdf_path.split("/")[-1].replace(".pdf", f".{output}")
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
    input,
    output: RAG_OutputType = RAG_OutputType.PDF,
    ocr=None,
    language: list = ["ch_sim", "en"],
    GPU: bool = False,
    path: str = "./Output",
    version: OutputVersion = OutputVersion.V1,
):
    """
    Args:
        `input`: input file path, str or list
        `output`: `str`, the type of output, "texts" "md" or "pdf", default is "pdf"
        `ocr`:  `function`, custom ocr function, not define will use easyocr.
        Or use `string`: `pytesseract` to use pytesseract, string `pass` to skip OCR
        `language`: list, the language used in OCR, default is ["ch_sim", "en"] for easyocr, ["eng"] for pytesseract
        `GPU`: `bool`, whether to use GPU in OCR, default is False, not working for pytesseract
        `path`: `str`, the path of folder to save the output, default is "./Output", only used when output is "md" or "pdf"
        `version`: `str`,If version is `v2`, will return more information, default is `v1`
    Returns:
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
        if not input.endswith(".pdf"):
            RuntimeError("The input must be path to a PDF file")
        input = [input]

    success_file = []
    failed_file = []
    error_flag = False
    for pdf_path in input:
        try:
            output_path, All_Done = deal_pdf_back(
                pdf_path, output, ocr, language, GPU, path, version
            )
            success_file.append(output_path)
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
            All_Done = True # * As this flag is use to determine if the OCR is done, we set it to True here
            success_file.append("")
            failed_file.append({"error": str(e), "file": pdf_path})
            error_flag = True
    print(
        f"PDFDEAL Progress: {sum(1 for s in success_file if s != '')}/{len(input)} files successfully processed."
    )
    if All_Done is False:
        print(
            "Some pictures are failed to OCR, but the text and reset pictures is extracted"
        )
    if error_flag:
        for f in failed_file:
            if f["error"] != "":
                print(f"-----\nFailed to process file: {f['file']} with error: {f['error']}\n-----")
    if version == "v2":
        return success_file, failed_file, error_flag
    return success_file
