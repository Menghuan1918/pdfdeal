"""Modular pdf file recognition engine"""

from typing import Tuple

BUILD_IN_TOOL = ["doc2x_pdf"]


def load_build_in_tool(tool: str):
    """
    Load the build-in tool engine

    Args:
        tool: The name of the tool engine, support `doc2x_pdf`

    Returns:
        tool, config, get
    """
    tool_mapping = {"doc2x_pdf": Tool_doc2x}
    tool_init = tool_mapping.get(tool)
    return tool_init()


def Tool_doc2x() -> Tuple[list, list, bool]:
    """
    deal pdf file with Doc2X

    Returns:
        tool, config, get
    """
    from .Tool.doc2x import tool, config, get

    return tool, config, get
