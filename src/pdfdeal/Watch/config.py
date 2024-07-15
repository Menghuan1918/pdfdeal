import os
import curses

from typing import Tuple
from ..FileTools.ocr import BUILD_IN_OCR
from ..FileTools.tool import BUILD_IN_TOOL
from .i18n import LANGUAGES, WORDS, WORDS_LOCAL
from .connect import BUILD_IN_CONNECT, load_build_in_connect


def init_config(language: str = None) -> dict:
    """This function is used to initialize the configuration of the program."""
    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    words = WORDS[language]

    all_option = [f"OCR: {ocr}" for ocr in BUILD_IN_OCR] + [
        f"Tool: {tool}" for tool in BUILD_IN_TOOL
    ]
    option1 = all_option[curses_select(all_option, words[0])]
    all_option.remove(option1)
    option1 = option1.split(":")[1].strip()
    all_option.append("OCR: pass")
    option2 = all_option[curses_select(all_option, words[1])]
    option2 = option2.split(":")[1].strip()
    Config = {"option1": option1, "option2": option2}

    # If select needs API
    if "doc2x" in option1 or "doc2x" in option2:
        Key, RPM = doc2x_api(words)
        Config["Doc2X_Key"] = Key
        Config["Doc2X_RPM"] = RPM

    return Config


def init_local_config(language: str = None, folder_name=None) -> Tuple[str, dict]:
    """This function is used to initialize the configuration of the local project folder."""
    from .store import get_global_setting

    if language is None:
        language = curses_select(LANGUAGES, "Please select the language:")
    words = WORDS_LOCAL[language]
    base_folder = os.path.expanduser("~/pdfdeal")
    if folder_name is None:
        while True:
            folder_name = input(words[0])
            folder = os.path.join(base_folder, folder_name)
            if os.path.exists(folder):
                print(words[1])
            else:
                break
    try:
        config = get_global_setting()
        if curses_select(["Yes", "No"], words[3]) == 1:
            raise FileNotFoundError
    except FileNotFoundError:
        config = init_config(language)
    print(words[2])
    print(folder)
    os.makedirs(folder)
    connect = curses_select(BUILD_IN_CONNECT, words[4])
    config_init_fnc = load_build_in_connect(BUILD_IN_CONNECT[connect])
    _, config_fnc = config_init_fnc()
    connect_config = config_fnc()
    config.update(connect_config)
    return folder_name, config


def curses_select(selects: list, show: str) -> int:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    try:
        current_row = 0
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(0, 0, show[: w - 1])
            for idx, item in enumerate(selects):
                x = max(0, w // 4 - len(item) // 2)
                y = h // 4 + idx
                if y >= h:
                    break
                item = item[: w - x - 1]
                if idx == current_row:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, x, item)
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, item)
            key = stdscr.getch()
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(selects) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return current_row
            elif key == curses.KEY_UP and current_row == 0:
                current_row = len(selects) - 1
            elif key == curses.KEY_DOWN and current_row == len(selects) - 1:
                current_row = 0
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


def doc2x_api(words: list) -> Tuple[str, int]:
    """This function is used to initialize the API key of doc2x."""
    from ..doc2x import Doc2X

    Key = input(words[2])
    try:
        Doc2X(Key)
    except Exception as e:
        raise Exception(f"{words[3]}:\n {e}")
    RPM = input(words[4])
    assert RPM.isdigit() or RPM == "A" or RPM == "a", "The input is invalid."
    if RPM == "A" or RPM == "a":
        if Key.startswith("sk-"):
            RPM = 10
        else:
            RPM = 1
    return Key, int(RPM)
