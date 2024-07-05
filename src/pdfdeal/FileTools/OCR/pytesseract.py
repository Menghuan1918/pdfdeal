import os
from typing import Tuple

def OCR_pytesseract(path, language=["eng"], GPU=False) -> Tuple[str, bool]:
    """
    OCR with pytesseract
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
