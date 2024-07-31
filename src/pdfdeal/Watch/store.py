import os
import json


def set_global_setting():
    """Set the global setting for pdfdeal"""
    from .config import init_config

    base_folder = os.path.expanduser("~/pdfdeal")
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    config = init_config()
    with open(global_setting_file, "w") as file:
        json.dump(config, file)


def change_one_global_setting(key: str, value: str):
    """Change one global setting or add a new one if not exist"""
    try:
        global_setting = get_global_setting()
    except FileNotFoundError:
        global_setting = {}
    global_setting[key] = value
    base_folder = os.path.expanduser("~/pdfdeal")
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    os.makedirs(base_folder, exist_ok=True)
    with open(global_setting_file, "w") as file:
        json.dump(global_setting, file)
    print("✅ Done!")


def delete_one_global_setting(key: str):
    """Delete one global setting"""
    global_setting = get_global_setting()
    if key in global_setting:
        del global_setting[key]
    base_folder = os.path.expanduser("~/pdfdeal")
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    with open(global_setting_file, "w") as file:
        json.dump(global_setting, file)
    print("✅ Done!")


def get_global_setting() -> dict:
    """Get the global setting for pdfdeal"""
    base_folder = os.path.expanduser("~/pdfdeal")
    global_setting_file = os.path.join(base_folder, "global_setting.json")
    if not os.path.exists(global_setting_file):
        raise FileNotFoundError(
            "The global setting file does not exist, please set the global setting first."
        )
    with open(global_setting_file, "r") as file:
        global_setting = json.load(file)
    return global_setting


def set_local_setting(folder_name: str = None):
    """Set the local setting for pdfdeal"""
    from .config import init_local_config

    base_folder = os.path.expanduser("~/pdfdeal")
    folder_name, local_config = init_local_config(folder_name=folder_name)
    local_setting_file = os.path.join(base_folder, folder_name, "local_setting.json")
    with open(local_setting_file, "w") as file:
        json.dump(local_config, file)
    print("✅ Done!")
