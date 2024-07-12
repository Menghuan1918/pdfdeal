"""Modular ocr engines"""

from typing import Tuple

BUILD_IN_OCR = ["doc2x_ocr", "easyocr", "pytesseract"]


def load_build_in_ocr(ocr: str):
    """
    Load the build-in OCR engine

    Args:
        ocr: The name of the OCR engine, support `doc2x_ocr`, `easyocr`, `pytesseract`, `pass`

    Returns:
        ocr, config, get
    """
    ocr_mapping = {
        "doc2x_ocr": OCR_pass,
        "easyocr": OCR_easyocr,
        "pytesseract": OCR_pytesseract,
    }
    ocr_init = ocr_mapping.get(ocr, OCR_pass)
    return ocr_init()


def OCR_easyocr() -> Tuple[str, bool]:
    """
    OCR with easyocr

    Returns:
        ocr, config, get
    """
    from .OCR.easyocr import ocr, config, get

    return ocr, config, get


def OCR_pytesseract():
    """
    OCR with pytesseract

    Returns:
        ocr, config, get
    """
    from .OCR.pytesseract import ocr, config, get

    return ocr, config, get


def OCR_pass():
    """
    Pass the OCR process

    Returns:
        ocr, config, get
    """
    from .OCR.passocr import ocr, config, get

    return ocr, config, get


def Doc2X_OCR():
    """
    OCR with Doc2X, `ocr` function's `options` args need a dict `{"Doc2X_Key": key, "Doc2X_RPM": int(RPM)}`

    Returns:
        ocr, config, get
    """
    from .OCR.doc2x import ocr, config, get

    return ocr, config, get
