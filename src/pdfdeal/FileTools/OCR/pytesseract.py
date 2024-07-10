"""Connect to local tesseract OCR"""

import os
from typing import Tuple


def ocr(path, language=["eng"], options: dict = None) -> Tuple[str, bool]:
    """Do OCR with tesseract

    Args:
        path (str): The path to pictures folder or a picture
        language (list, optional): The language use for tesseract, only first one will use. Defaults to ["eng"].
        options (dict, optional): No need for tesseract. Defaults to None.

    Raises:
        ImportError: If not install `pytesseract`

    Returns:
        Tuple[str, bool]:  The OCR text and if all the files are done
    """
    try:
        import pytesseract
    except ImportError:
        raise ImportError(
            "Please install pytesseract first, use 'pip install pytesseract'"
        )
    text = ""
    All_Done = True
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        try:
            text += pytesseract.image_to_string(path, lang=language[0])
            text += "\n"
        except Exception as e:
            print(
                f"Get error when using pytesseract to do ocr and pass to next file. {e}"
            )
            All_Done = False
            pass
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    try:
                        text += pytesseract.image_to_string(file_path, lang=language[0])
                        text += "\n"
                    except Exception as e:
                        print(
                            f"Get error when using pytesseract to do ocr and pass to next file. {e}"
                        )
                        All_Done = False
                        pass
    return text, All_Done


def config(language: str = None) -> dict:
    return {}


def get() -> dict:
    return None
