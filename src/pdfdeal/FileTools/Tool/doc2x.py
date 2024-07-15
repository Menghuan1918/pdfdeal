"""Connect to Doc2X API to deal with pdf file."""

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


def tool(path: str, options: dict) -> Tuple[list, list, bool]:
    """
    deal pdf file with Doc2X
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

    return Client.pdfdeal(pdf_file=path, output_path=options["output"], convert=False)


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
