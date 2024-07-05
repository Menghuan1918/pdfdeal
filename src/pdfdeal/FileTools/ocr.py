"""Modular ocr engines"""

from typing import Tuple

BUILD_IN_OCR = ["doc2x", "easyocr", "pytesseract"]


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
