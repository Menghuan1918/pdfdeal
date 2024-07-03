from pdfdeal import gen_folder_list as gfl
import warnings

def gen_folder_list(
        path: str,
        mode: str,
)->list:
    """
    This function will be deprecated in the future, please use `from pdfdeal import gen_folder_list` instead.
    """
    warnings.warn("This function will be deprecated in the future, please use `from pdfdeal import gen_folder_list` instead.", DeprecationWarning)
    return gfl(path, mode)