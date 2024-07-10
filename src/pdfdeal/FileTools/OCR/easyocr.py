import os
from typing import Tuple

LANGUAGES = ["简体中文", "Enlish"]
WORDS_CN = ["🔌 是否使用GPU加速？注意easyocr仅支持CUDA加速："]
WORDS_EN = [
    "🔌 Do you want to use GPU acceleration? Note that easyocr only supports CUDA acceleration:"
]
WORDS = [WORDS_CN, WORDS_EN]


def ocr(path, language=["auto"], options: dict = None) -> Tuple[str, bool]:
    """Do OCR with easyocr

    Args:
        path (str): The path to pictures folder or a picture
        language (list, optional): Language use. Defaults to ["auto"].
        options (dict, optional): Need `{"GPU": bool}`. Defaults is `{"GPU": False}`

    Raises:
        ImportError: If not install `easyocr`

    Returns:
        Tuple[str, bool]: The OCR text and if all the files are done
    """
    try:
        import easyocr
    except ImportError:
        raise ImportError("Please install easyocr first, use 'pip install easyocr'")
    GPU = options.get("gpu", False)
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


def config(language: str = None) -> dict:
    """Get the config of easyocr"""
    from ...Watch.config import curses_select

    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    words = WORDS[language]
    gpu = curses_select(["❎ No", "✅ Yes"], words[0])
    if gpu == "✅ Yes":
        return {"GPU": True}
    return {"GPU": False}


def get(config: dict) -> dict:
    """Get the config of easyocr"""
    try:
        return {"GPU": config["GPU"]}
    except KeyError:
        raise KeyError("The configuration is invalid, please check the configuration")
