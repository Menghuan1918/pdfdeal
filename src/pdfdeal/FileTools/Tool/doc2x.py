from typing import Tuple, Callable


def Doc2X_Tool(Client) -> Callable:
    """
    deal pdf file with Doc2X
    """
    try:
        limit = Client.get_limit()
    except Exception as e:
        raise Exception(f"Get error! {e}")
    if limit == 0:
        raise Exception("The Doc2X limit is 0, please check your account.")

    def Tool(path: str, options: dict) -> Tuple[list, list, bool]:
        return Client.pdfdeal(input=path, path=options["output"], version="v2")

    return Tool
