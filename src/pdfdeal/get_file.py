import requests
import os
from .file_tools import extract_text_and_images
from .file_tools import OCR_easyocr
from .file_tools import OCR_pytesseract
from .file_tools import OCR_pass
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def download_pdfs_from_url(url):
    temp_pdf_path = os.path.join(os.path.expanduser("~"), ".cache", "pdfdeal")
    os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
    headers = requests.utils.default_headers()

    headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
    )
    filename = url.split("/")[-1]
    temp_pdf_path = os.path.join(temp_pdf_path, filename)
    try:
        with requests.get(url, headers=headers) as response:
            with open(temp_pdf_path, "wb") as file:
                file.write(response.content)
    except Exception as e:
        print(f"Failed to download the PDF file from {url}")
        print(f"Error: {e}")
        return None
    return temp_pdf_path


def strore_pdf(pdf_path, Text):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    for text in Text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            c.drawString(100, 750 - i * 13, line)
        c.showPage()
    c.save()


def deal_pdf(
    input, output="text", ocr=None, language=["ch_sim", "en"], GPU=False, path=None
):
    """
    input: str, the url or path to a PDF file
    output: str, the type of output, "text" "texts" "md" or "pdf", default is "text"
    ocr: function, custom ocr function, not define will use easyocr, string "pytesseract" to use pytesseract, string "pass" to skip OCR
    language: list, the language used in OCR, default is ["ch_sim", "en"] for easyocr, ["eng"] for pytesseract
    GPU: bool, whether to use GPU in OCR, default is False, not working for pytesseract
    path: str, the path of folder to save the output, default is None, only used when output is "md" or "pdf"
    """
    if isinstance(input, str):
        if not input.endswith(".pdf"):
            RuntimeError("The input must be a string of url or path to a PDF file")
        elif input.startswith("http") and input.endswith(".pdf"):
            pdf_path = download_pdfs_from_url(input)
        else:
            pdf_path = input
    else:
        RuntimeError("The input must be a string or url or path to a PDF file")
    if ocr is None:
        Text = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_easyocr, language=language, GPU=GPU
        )
    elif ocr == "pytesseract":
        Text = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_pytesseract, language=language, GPU=GPU
        )
    elif ocr == "pass":
        Text = extract_text_and_images(
            pdf_path=pdf_path, ocr=OCR_pass, language=language, GPU=GPU
        )
    else:
        Text = extract_text_and_images(
            pdf_path=pdf_path, ocr=ocr, language=language, GPU=GPU
        )
    Final = ""
    if output == "texts":
        return Text
    elif output == "text":
        for text in Text:
            Final += text + "\n"
        return Final
    else:
        filename = pdf_path.split("/")[-1].replace(".pdf", f".{output}")
        if path is None:
            path = os.path.join(os.getcwd(), "output")
        if not os.path.exists(path):
            os.makedirs(path)
        if output == "md":
            try:
                with open(os.path.join(path, filename), "w") as file:
                    for text in Text:
                        file.write(text + "\n")
                return os.path.join(path, filename)
            except Exception as e:
                RuntimeError(f"Failed to save the markdown file: {e}")
        elif output == "pdf":
            output_pdf_path = os.path.join(path, filename)
            try:
                strore_pdf(output_pdf_path, Text)
                return output_pdf_path
            except Exception as e:
                RuntimeError(f"Failed to save the PDF file: {e}")
