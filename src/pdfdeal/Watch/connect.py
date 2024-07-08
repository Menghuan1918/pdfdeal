"""The connect funcs of the project"""


def local_folder_connect():
    """Connect to a local folder"""
    from .Connect.local import connect, config

    return connect, config
