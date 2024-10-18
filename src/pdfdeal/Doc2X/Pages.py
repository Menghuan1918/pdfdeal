from pypdf import PdfReader
from .Exception import RequestError


def get_pdf_page_count(pdf_path: str) -> int:
    """
    Get the number of pages in a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        int: The number of pages in the PDF.
    """
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        pages = len(reader.pages)
    if pages > 1000:
        raise RequestError("parse_file_page_limit")
    return pages
