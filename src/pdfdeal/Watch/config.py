import os
import curses

from ..FileTools.ocr import BUILD_IN_OCR
from ..FileTools.tool import BUILD_IN_TOOL
from .i18n import LANGUAGES, WORDS

def init_config():
    """This function is used to initialize the configuration of the program."""
    Language = curses_select(LANGUAGES, "Please select the language:")
    Words = WORDS[Language]

    all_option = [f"OCR: {ocr}" for ocr in BUILD_IN_OCR] + [
        f"Tool: {tool}" for tool in BUILD_IN_TOOL
    ]
    option1 = all_option[curses_select(all_option, Words[0])]
    all_option.remove(option1)
    option1 = option1.split(":")[1].strip()
    all_option.append("OCR: pass")
    option2 = all_option[curses_select(all_option, Words[1])]
    option2 = option2.split(":")[1].strip()
    Config = {"option1": option1, "option2": option2}

    # If select needs API
    if "doc2x" in option1 or "doc2x" in option2:
        Key, RPM = doc2x_api(Words)
        Config["Key"] = Key
        Config["RPM"] = RPM

    return Config


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
            stdscr.addstr(0, 0, show)
            for idx, item in enumerate(selects):
                x = w // 4 - len(item) // 2
                y = 4 + idx
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


def doc2x_api(Words: list):
    """This function is used to initialize the API key of doc2x."""
    from ..doc2x import Doc2X

    Key = input(Words[2])
    try:
        Doc2X(Key)
    except Exception as e:
        raise Exception(f"{Words[3]}:\n {e}")
    RPM = input(Words[4])
    assert RPM.isdigit() or RPM == "A" or RPM == "a", "The input is invalid."
    if RPM == "A" or RPM == "a":
        if Key.startswith("sk-"):
            RPM = 10
        else:
            RPM = 4
    return Key, RPM
