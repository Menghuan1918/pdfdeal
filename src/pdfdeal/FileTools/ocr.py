"""Modular ocr engines"""

from typing import Tuple

BUILD_IN_OCR = ["doc2x_ocr", "easyocr", "pytesseract"]

def load_build_in_ocr(ocr: str):
    """
    Load the build-in OCR engine
    """
    ocr_mapping = {
        "doc2x_ocr": OCR_pass,
        "easyocr": OCR_easyocr,
        "pytesseract": OCR_pytesseract
    }
    return ocr_mapping.get(ocr, OCR_pass)

def OCR_easyocr(path, language=["ch_sim", "en"], GPU=False) -> Tuple[str, bool]:
    """
    OCR with easyocr
    """
    from .OCR.easyocr import OCR_easyocr

    return OCR_easyocr(path, language, GPU)


def OCR_pytesseract(path, language=["eng"], GPU=False) -> Tuple[str, bool]:
    """
    OCR with pytesseract
    """
    from .OCR.pytesseract import OCR_pytesseract

    return OCR_pytesseract(path, language, GPU)


def OCR_pass(path, language=["ch_sim", "en"], GPU=False) -> Tuple[str, bool]:
    """
    Pass the OCR process
    """
    return "", True


def Doc2X_OCR(Client):
    """
    OCR with Doc2X
    """
    from .OCR.doc2x import Doc2X_OCR

    return Doc2X_OCR(Client)
