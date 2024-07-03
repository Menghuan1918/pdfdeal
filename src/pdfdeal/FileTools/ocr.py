import os

def OCR_easyocr(path, language=["ch_sim", "en"], GPU=False):
    """
    OCR with easyocr
    """
    try:
        import easyocr
    except ImportError:
        raise ImportError("Please install easyocr first, use 'pip install easyocr'")
    reader = easyocr.Reader(language, gpu=GPU)
    texts = ""
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        try:
            result = reader.readtext(path, detail=0, paragraph=True)
        except Exception:
            result = [""]
        texts += "\n".join(result)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    try:
                        result = reader.readtext(file_path, detail=0, paragraph=True)
                    except Exception:
                        result = [""]
                    texts += "\n".join(result)
    return texts


def OCR_pytesseract(path, language=["eng"], GPU=False):
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
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        try:
            text += pytesseract.image_to_string(path, lang=language[0])
            text += "\n"
        except Exception:
            pass
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    try:
                        text += pytesseract.image_to_string(file_path, lang=language[0])
                        text += "\n"
                    except Exception:
                        pass
    return text


def OCR_pass(path, language=["ch_sim", "en"], GPU=False):
    """
    Pass the OCR process
    """
    return ""