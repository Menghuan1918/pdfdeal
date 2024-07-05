"""Modular pdf file recognition engine"""

from typing import Tuple

BUILD_IN_TOOL = ["doc2x"]


def Tool_doc2x(Client) -> Tuple[list, list, bool]:
    """
    deal pdf file with Doc2X
    """
    from .Tool.doc2x import Doc2X_Tool

    return Doc2X_Tool(Client)
