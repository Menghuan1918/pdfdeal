"""Modular pdf file recognition engine"""

from typing import Tuple

BUILD_IN_TOOL = ["doc2x_pdf"]

def load_build_in_tool(tool: str):
    """
    Load the build-in tool engine
    """
    tool_mapping = {
        "doc2x_pdf": Tool_doc2x
    }
    return tool_mapping.get(tool)


def Tool_doc2x(Client) -> Tuple[list, list, bool]:
    """
    deal pdf file with Doc2X
    """
    from .Tool.doc2x import Doc2X_Tool

    return Doc2X_Tool(Client)
