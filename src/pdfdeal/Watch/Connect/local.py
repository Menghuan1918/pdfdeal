"""Connect to a local directory"""

import logging
from typing import Tuple
import shutil
import os

LANGUAGES = ["简体中文", "Enlish"]
WORDS_CN = [
    "📂 请输入目输出的目标文件路径：",
    "📦 目录不存在，是否创建？[Y/n]：",
    "⚠️ 目标必须是一个文件夹",
    "⚠️ 没有目标文件夹的写入权限，请确保您有写入权限",
    "⚠️ 目录不为空，请输入一个空目录",
]
WORDS_EN = [
    "📂 Please enter the target file path:",
    "📦 The directory does not exist, do you want to create it? [Y/n]:",
    "⚠️ The target must be a directory",
    "⚠️ No write permission for the target directory, please make sure you have write permission",
    "⚠️ The directory is not empty, please enter an empty directory",
]
WORDS = [WORDS_CN, WORDS_EN]


def connect(file_list: list, base_path: str, options: dict) -> Tuple[list, list, bool]:
    """Connect to a local directory"""
    target_path = options["target_path"]
    success = []
    faied = []
    flag = False
    for file in file_list:
        try:
            shutil.move(os.path.join(base_path, file), os.path.join(target_path, file))
            success.append(file)
            faied.append({"error": "", "path": ""})
            logging.info(f"Succeed to move {file} to {target_path}")
        except Exception as e:
            success.append("")
            faied.append({"error": str(e), "path": file})
            flag = True
            logging.error(f"Failed to move {file} to {target_path}, error: {str(e)}")
    return success, faied, flag


def config(language: str = None) -> dict:
    """Set the configuration of the local directory"""
    from ..config import curses_select

    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    words = WORDS[language]
    while True:
        target_path = input(words[0])
        if not os.path.exists(target_path):
            if input(words[1]).lower() != "n":
                os.makedirs(target_path)
                break
        else:
            # Check the target path
            if not os.path.isdir(target_path):
                raise NotADirectoryError(words[2])
            # Check the permission of the target path
            try:
                with open(os.path.join(target_path, "test"), "w"):
                    pass
                os.remove(os.path.join(target_path, "test"))
            except PermissionError:
                raise PermissionError(words[3])
            # Check the content of the target path
            if os.listdir(target_path):
                raise FileExistsError(words[4])
    return {"target_path": os.path.abspath(target_path)}


def get(config: dict) -> str:
    """Get the option setting from the configuration"""
    try:
        return {"target_path": config["target_path"]}
    except KeyError:
        raise KeyError("The configuration is invalid, please check the configuration")
