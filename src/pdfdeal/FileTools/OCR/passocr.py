"""Just pass the OCR process."""

from typing import Tuple


def ocr(path, language=["auto"], options: dict = None) -> Tuple[str, bool]:
    return "", True


def config(language: str = None) -> dict:
    return {}


def get() -> dict:
    return None
