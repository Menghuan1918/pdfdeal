"""Connect to Doc2X OCR API"""

from PIL import Image
import os
from typing import Tuple

LANGUAGES = ["简体中文", "Enlish"]
WORDS_CN = [
    "📇 请输入 Doc2X 的身份令牌，个人用户请访问 https://doc2x.noedgeai.com/ 获取：",
    "⚠️ 验证 Doc2X 的身份令牌失败，请检查网络连接或者身份令牌是否正确",
    "📌 请选择 Doc2X 的速率限制，含意为同时请求数量，建议输入 A 以自动选择速率限制：",
]
WORDS_EN = [
    "📇 Please enter the API key of the Doc2X, for personal use, visit https://doc2x.com/ to get the key:",
    "⚠️ Failed to verify the API key of Doc2X, please check the network connection or the API key",
    "📌 Please select the rate limit of Doc2X, means number of simultaneous requests, it is recommended to enter A to automatically select the rate limit:",
]
WORDS = [WORDS_CN, WORDS_EN]


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


def ocr(path, language=["auto"], options: dict = None) -> Tuple[str, bool]:
    """Do OCR with Doc2X

    Args:
        path (str): The path to pictures folder or a picture
        language (list, optional): No need for Doc2X
        options (dict, must): Need `{"Doc2X_Key": key, "Doc2X_RPM": RPM}`

    Raises:
        Exception: If the Doc2X limit is 0
        Exception: If the number of files in the folder exceeds the limit
        Exception: If the input is invalid

    Returns:
        Tuple[str, bool]: The OCR text and if all the files are done
    """
    from pdfdeal import Doc2X

    api_key = options["api_key"]
    rpm = options.get("rpm", None)
    if rpm is None:
        Client = Doc2X(apikey=api_key)
    else:
        Client = Doc2X(apikey=api_key, thread=rpm)

    try:
        limit = Client.get_limit()
    except Exception as e:
        raise Exception(f"Get error! {e}")
    if limit == 0:
        raise Exception("The Doc2X limit is 0, please check your account.")

    text = ""
    All_Done = True
    if os.path.isfile(path) and path.endswith((".jpg", ".png", ".jpeg")):
        try:
            equation = doc2x_judgements(image_file=path)
            texts, Failed, Fail_flag = Client.pic2file(
                image_file=path,
                output_format="txts",
                equation=equation,
            )
            for t in texts:
                text += t + "\n"
            if Fail_flag:
                for fail in Failed:
                    if fail["error"] != "":
                        print(f"Get error when using Doc2X to do ocr. {fail['error']}")
                All_Done = False
        except Exception as e:
            print(f"Get error when using Doc2X to do ocr and pass to next file. {e}")
            All_Done = False
            pass
    elif os.path.isdir(path):
        file_count = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith((".jpg", ".png", ".jpeg")):
                    file_count += 1
        if file_count > limit:
            raise Exception(
                f"The number of files in the folder exceeds the limit, please check the folder: {path}"
            )

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


def config(language: str = None) -> dict:
    """Set the configuration of the local directory"""
    from ...Watch.config import curses_select

    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    words = WORDS[language]
    key = input(words[0])
    from pdfdeal import Doc2X

    try:
        Doc2X(apikey=key)
    except Exception as e:
        raise Exception(f"{words[1]}:\n {e}")
    RPM = input(words[2])
    assert RPM.isdigit() or RPM == "A" or RPM == "a", "The input is invalid."
    if RPM == "A" or RPM == "a":
        if key.startswith("sk-"):
            RPM = 10
        else:
            RPM = 1
    return {"Doc2X_Key": key, "Doc2X_RPM": int(RPM)}


def get(config: dict) -> dict:
    """Get the option setting from the configuration"""
    try:
        return {"api_key": config["Doc2X_Key"], "rpm": config["Doc2X_RPM"]}
    except KeyError:
        raise KeyError("The configuration is invalid, please check the configuration")
