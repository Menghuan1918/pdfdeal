from PIL import Image
import os
from typing import Tuple

def doc2x_judgements(image_file):
    """
    Whether the image is samll enough to be enable purely formulaic model
    """
    with Image.open(image_file) as img:
        size = img.size
    if size[0] < 50 and size[1] < 50:
        return 1
    else:
        return 0
    
def Doc2X_OCR(Client):
    """
    OCR with Doc2X
    """
    try:
        limit = Client.get_limit()
    except Exception as e:
        raise Exception(f"Get error! {e}")
    if limit == 0:
        raise Exception("The Doc2X limit is 0, please check your account.")

    def OCR(path, language=["ch_sim", "en"], GPU=False) -> Tuple[str, bool]:
        text = ""
        All_Done = True
        if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
            try:
                equation = doc2x_judgements(image_file=path)
                texts, Failed, Fail_flag = Client.pic2file(
                    image_file=path,
                    output_format="txts",
                    equation=equation,
                    version="v2",
                )
                for t in texts:
                    text += t + "\n"
                if Fail_flag:
                    for fail in Failed:
                        if fail["error"] != "":
                            print(
                                f"Get error when using Doc2X to do ocr. {fail['error']}"
                            )
                    All_Done = False
            except Exception as e:
                print(
                    f"Get error when using Doc2X to do ocr and pass to next file. {e}"
                )
                All_Done = False
                pass
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith((".jpg", ".png", ".jpeg")):
                        try:
                            # * Since the size and dimensions of each image may be different, batch processing mode is not used
                            equation = doc2x_judgements(image_file=file_path)
                            texts, Failed, Fail_flag = Client.pic2file(
                                image_file=path,
                                output_format="txts",
                                equation=equation,
                                version="v2",
                            )
                            for t in texts:
                                text += t + "\n"
                            if Fail_flag:
                                for fail in Failed:
                                    if fail["error"] != "":
                                        print(
                                            f"Get error when using Doc2X to do ocr. {fail['error']}"
                                        )
                                All_Done = False
                        except Exception as e:
                            print(
                                f"Get error when using Doc2X to do ocr and pass to next file. {e}"
                            )
                            All_Done = False
                            pass
        return text, All_Done

    return OCR
