import os
from typing import Tuple


def OCR_easyocr(path, language=["ch_sim", "en"], GPU=False) -> Tuple[str, bool]:
    """
    OCR with easyocr
    """
    try:
        import easyocr
    except ImportError:
        raise ImportError("Please install easyocr first, use 'pip install easyocr'")
    reader = easyocr.Reader(language, gpu=GPU)
    All_Done = True
    texts = ""
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        try:
            result = reader.readtext(path, detail=0, paragraph=True)
        except Exception as e:
            result = [""]
            All_Done = False
            print(f"Get error when using easyocr to do ocr and pass to next file. {e}")
        texts += "\n".join(result)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith((".jpg", ".png", ".jpeg")):
                    try:
                        result = reader.readtext(file_path, detail=0, paragraph=True)
                    except Exception as e:
                        result = [""]
                        All_Done = False
                        print(
                            f"Get error when using easyocr to do ocr and pass to next file. {e}"
                        )
                    texts += "\n".join(result)
    return texts, All_Done
