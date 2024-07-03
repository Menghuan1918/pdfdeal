import os
from PIL import Image
from ..doc2x import Doc2X


def doc2x_judgements(image_file):
    """
    Whether the image is samll enough to be enable purely formulaic model
    """
    with Image.open(image_file) as img:
        size = img.size
    if size[0] < 100 and size[1] < 100:
        return 1
    else:
        return 0


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
        except Exception as e:
            result = [""]
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
                        print(
                            f"Get error when using easyocr to do ocr and pass to next file. {e}"
                        )
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
        except Exception as e:
            print(
                f"Get error when using pytesseract to do ocr and pass to next file. {e}"
            )
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
                        pass
    return text


def OCR_pass(path, language=["ch_sim", "en"], GPU=False):
    """
    Pass the OCR process
    """
    return ""


def Doc2X_OCR(Client: Doc2X):
    """
    OCR with Doc2X
    """
    try:
        limit = Client.get_limit()
    except Exception as e:
        raise Exception(f"Get error! {e}")
    if limit == 0:
        raise Exception("The OCR limit is 0, please check your account.")

    def OCR(path, language=["ch_sim", "en"], GPU=False):
        text = ""
        if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
            try:
                equation = doc2x_judgements(image_file=path)
                texts = Client.pic2file(
                    image_file=path, output_format="txts", equation=equation
                )
                for t in texts:
                    text += t + "\n"
            except Exception as e:
                print(
                    f"Get error when using Doc2X to do ocr and pass to next file. {e}"
                )
                pass
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith((".jpg", ".png", ".jpeg")):
                        try:
                            # * Since the size and dimensions of each image may be different, batch processing mode is not used
                            equation = doc2x_judgements(image_file=file_path)
                            texts = Client.pic2file(
                                image_file=file_path,
                                output_format="txts",
                                equation=equation,
                                version="v1",
                            )
                            for t in texts:
                                text += t + "\n"
                        except Exception as e:
                            print(
                                f"Get error when using Doc2X to do ocr and pass to next file. {e}"
                            )
                            pass
        return text

    return OCR
