import argparse
from pdfdeal.Watch.store import (
    get_global_setting,
    change_one_global_setting,
    delete_one_global_setting,
)
import os
from pdfdeal import Doc2X
from pdfdeal.file_tools import get_files
from pdfdeal.Watch.config import curses_select
import logging

LANGUAGES = ["简体中文", "Enlish"]
WORDS_CN = [
    "📇 请输入 Doc2X 的身份令牌，个人用户请访问 https://doc2x.noedgeai.com/ 获取, 将会自动保存至本地：",
    "⚠️ 验证 Doc2X 的身份令牌失败，请检查网络连接或者身份令牌是否正确",
    "📌 请选择 Doc2X 的速率限制，含意为同时请求数量，强烈建议输入 A 以自动选择速率限制：",
    "🚧 请选择要处理的文件类型:",
    "📂 请输入要处理的文件或文件夹：",
    "⚠️ 未找到所在文件或文件夹",
]
WORDS_EN = [
    "📇 Please enter the API key of the Doc2X, for personal use, visit https://doc2x.com/ to get the key, will auto save to local:",
    "⚠️ Failed to verify the API key of Doc2X, please check the network connection or the API key",
    "📌 Please select the rate limit of Doc2X, means number of simultaneous requests, it is recommended to enter A to automatically select the rate limit:",
    "🚧 Please select the type of file to process:",
    "📂 Please enter the file or folder to deal with:",
    "⚠️ The file or folder does not exist",
]
WORDS = [WORDS_CN, WORDS_EN]


def i18n(language):
    """Maybe the lazy i18n solution, but it works."""
    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    return WORDS[language], language


def set_doc2x_key(language):
    """Set the Doc2X key and rate limit."""
    words, language = i18n(language)
    key = input(words[0])
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
    return {"Doc2X_Key": key, "Doc2X_RPM": int(RPM)}, language


def get_file_folder(language):
    words, language = i18n(language)
    while True:
        file_folder = input(words[4])
        if os.path.exists(file_folder):
            break
        print(words[5])
    return file_folder, language


def file_type(language):
    words, language = i18n(language)
    file_type = curses_select(selects=["PDF", "Picture"], show=words[3])
    if file_type == 0:
        return False, True, language
    else:
        return True, False, language


def main():
    parser = argparse.ArgumentParser(
        description="Using doc2x to deal with pictures or pdfs"
    )
    parser.add_argument("filename", help="PDF or picture file/folder", nargs="?")
    parser.add_argument(
        "-y",
        help="Will skip any scenarios that require a second input from the user.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-k",
        "--api_key",
        help="The API key of Doc2X, if not set, will use the global setting",
        required=False,
    )
    parser.add_argument(
        "-r",
        "--rpm",
        help="The rate limit of Doc2X, DO NOT set if you don't know",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The output folder of the result, if not set, will set to './Output'",
        required=False,
    )
    parser.add_argument(
        "-f",
        "--format",
        help="The output format of the result, accept md、md_dollar、latex、docx, default is md_dollar",
        required=False,
        choices=["md", "md_dollar", "latex", "docx"],
    )
    parser.add_argument(
        "-i",
        "--image",
        help="If the input is a picture, set this flag to True, or will ask you",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--pdf",
        help="If the input is a pdf, set this flag to True, or will ask you",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--equation",
        help="Whether to use the equation model, only works for pictures, default is False",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--clear",
        help="Clear all the global setting about Doc2X",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--graphrag",
        help="Change md document to txt form, used for output is converted to the txt form accepted by graphRAG. The output format needs to be md or md_dollar at this time",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--unzip",
        help="Unzip the output file, only works for the output is zip file",
        required=False,
        action="store_true",
    )
    # Only if need user input, will ask language
    language = None
    args = parser.parse_args()
    rpm = None

    # logging set to info
    logging.basicConfig(level=logging.INFO)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)

    if args.clear:
        delete_one_global_setting("Doc2X_Key")
        delete_one_global_setting("Doc2X_RPM")
        print("Clear all the global setting.")

    if args.api_key is None:
        try:
            api_key = str(get_global_setting()["Doc2X_Key"])
            rpm = int(get_global_setting()["Doc2X_RPM"])
            print("Find API: ", api_key[:5] + "*" * (len(api_key) - 10) + api_key[-5:])
        except Exception:
            if args.y:
                pass
            else:
                api_key = None
                print(
                    "The global setting does not exist, please set the global setting first."
                )
                doc2x_setting, language = set_doc2x_key(language)
                for key, value in doc2x_setting.items():
                    change_one_global_setting(key, value)
                api_key = str(doc2x_setting["Doc2X_Key"])
                rpm = int(doc2x_setting["Doc2X_RPM"])
    else:
        api_key = str(args.api_key)

    if rpm is None:
        rpm = int(args.rpm) if args.rpm else 10 if api_key.startswith("sk-") else 1

    image = args.image
    pdf = args.pdf
    if not image and not pdf:
        if args.y:
            pdf = True
        else:
            image, pdf, language = file_type(language)
    if image and pdf:
        raise ValueError("You can only choose one type of file to process.")

    filename = args.filename

    if filename is None:
        if args.y:
            filename = "./"
        else:
            filename, language = get_file_folder(language)

    output = args.output if args.output else "./Output"

    format = args.format if args.format else "md_dollar"

    equation = args.equation

    if api_key is None or api_key == "":
        Client = Doc2X()
    else:
        Client = Doc2X(apikey=api_key, thread=rpm)

    if args.graphrag:
        assert format in [
            "md",
            "md_dollar",
        ], "The output format needs to be md or md_dollar at this time"

    if image:
        files, rename = get_files(filename, "img", format)
        success, fail, flag = Client.pic2file(
            image_file=files,
            output_path=output,
            output_names=rename,
            output_format=format,
            equation=equation,
        )

    if pdf:
        files, rename = get_files(filename, "pdf", format)
        success, fail, flag = Client.pdf2file(
            pdf_file=files,
            output_path=output,
            output_names=rename,
            output_format=format,
        )

    for file in success:
        if file != "":
            file = os.path.abspath(file)
            print(f"Save to: {file}")
    if flag:
        print("Some files failed to process, please check the error message.")
        print("Try to save the failed file path and reasons to fail.txt")
        try:
            with open("fail.txt", "w") as f:
                for file in fail:
                    if file["path"] != "":
                        f.write(str(file))
        except Exception as e:
            print(f"Failed to save the failed files to fail.txt: {e}")
            print("The failed files are:")
            for file in fail:
                print(file)

    if args.graphrag or args.unzip:
        from pdfdeal.FileTools.file_tools import unzip

        for file in success:
            if file != "" and file.endswith(".zip"):
                file = os.path.abspath(file)
                try:
                    unzip(zip_path=file, rename=True)
                except Exception as e:
                    print(f"Failed to unzip the file: {file}, error: {e}")
        output_folder = os.path.abspath(output)
        if args.graphrag:
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        new_file_path = file_path[:-3] + ".txt"
                        os.rename(file_path, new_file_path)
        print(f"Unzip and rename the files in {output_folder} successfully.")

    print(f"===\nLeft Doc2X pages: {Client.get_limit()}\n Have a nice day!")


if __name__ == "__main__":
    main()
