import os
import json


def set_global_setting():
    """Set the global setting for pdfdeal"""
    base_folder = os.path.expanduser("~"), "pdfdeal"
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    from .config import global_setting

    with open(global_setting_file, "w") as file:
        json.dump(global_setting, file)


def get_global_setting() -> dict:
    """Get the global setting for pdfdeal"""
    base_folder = os.path.expanduser("~"), "pdfdeal"
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    if not os.path.exists(global_setting_file):
        print(
            "The global setting file does not exist, please set the global setting first."
        )
    with open(global_setting_file, "r") as file:
        global_setting = json.load(file)
    return global_setting
