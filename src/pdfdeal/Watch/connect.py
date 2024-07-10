"""The connect funcs of the project"""

BUILD_IN_CONNECT = ["local_folder"]


def load_build_in_connect(connect: str):
    """
    Load the build-in connect engine
    """
    connect_mapping = {"local_folder": local_folder_connect}
    return connect_mapping.get(connect)


def local_folder_connect():
    """Connect to a local folder"""
    from .Connect.local import connect, config, get

    return connect, config, get
