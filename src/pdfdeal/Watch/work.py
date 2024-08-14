"""The main part of deal with the pdf files"""

import logging
import os

from ..FileTools.ocr import BUILD_IN_OCR, load_build_in_ocr
from ..FileTools.tool import BUILD_IN_TOOL, load_build_in_tool


def tools(tool: str, file_list: list, config: dict):
    #! Need to rewrite the dealpdf function
    temp_path = os.path.join(os.path.expanduser("~"), ".cache", "pdfdeal", "dealed")
    #! Not support the custom options now
    if tool not in BUILD_IN_TOOL:
        raise Exception(f"Tool {tool} is not supported.")
    tool_init_func = load_build_in_tool(tool)
    if tool == "doc2x_pdf":
        from pdfdeal import Doc2X

        Client = Doc2X(apikey=config["Doc2X_Key"], thread=config["Doc2X_RPM"])
        tool_func = tool_init_func(Client)
    options = {"output": temp_path}
    return tool_func(file_list, options)


def ocrs(ocr: str, config: dict):
    if ocr not in BUILD_IN_OCR:
        raise Exception(f"OCR {ocr} is not supported.")
    ocr_init_func = load_build_in_ocr(ocr)
    if ocr == "doc2x_ocr":
        from pdfdeal import Doc2X

        Client = Doc2X(apikey=config["Doc2X_Key"], thread=config["Doc2X_RPM"])
        return ocr_init_func(Client)
    return ocr_init_func


def option_part(tool_or_ocr: str, file_list: list, config: dict):
    """Do the main process of the program, do ocr or file tools.

    Args:
        tool_or_ocr (str): The name of the tool or ocr
        file_list (list): The list of the file path to deal with
        config (dict): The configuration of the program

    Returns:
        _type_: _description_
    """
    if tool_or_ocr in BUILD_IN_OCR:
        #! Need to rewrite the dealpdf function
        from pdfdeal import deal_pdf

        temp_path = os.path.join(os.path.expanduser("~"), ".cache", "pdfdeal", "dealed")
        ocr = ocrs(tool_or_ocr, config)
        success, fail, flag = deal_pdf(file_list, ocr=ocr, output_path=temp_path)
    else:
        success, fail, flag = tools(tool_or_ocr, file_list, config)
    return success, fail, flag


def main_process(file_list: list, config: dict):
    done_files = []
    success, fail, flag = option_part(config["option1"], file_list, config)
    if flag:
        logging.error("The first option failed, fallback to the second option.")
        done_files.extend([file for file in success if file != ""])
        failed_files = [file["path"] for file in fail]
        success, fail, flag = option_part(config["option2"], failed_files, config)
        if flag:
            logging.error("The second option failed, fallback to the pass OCR.")
            done_files.extend([file for file in success if file != ""])
            failed_files = [file["path"] for file in fail]
            success, fail, flag = option_part("pass", failed_files, config)
            done_files.extend([file for file in success if file != ""])
        else:
            done_files.extend(success)
    else:
        done_files.extend(success)
    return done_files
