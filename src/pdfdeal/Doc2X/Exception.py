import asyncio
from functools import wraps
import time
import sys
from concurrent.futures import ThreadPoolExecutor
import logging


class RateLimit(Exception):
    """
    Error when rate limit is reached.
    """

    pass


class RequestError(Exception):
    """
    Error when request is not successful, usually because of the file broken.
    """

    pass


class FileError(Exception):
    """
    Error when file is not found or cannot be opened or othes.
    """

    pass


def async_retry(max_retries=2, backoff_factor=2):
    """
    Decorator to retry an async function when an exception is raised.
    `max_retries`: Maximum number of retries.
    `backoff_factor`: Factor to increase the wait time between retries.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries + 1:
                try:
                    return await func(*args, **kwargs)
                except RateLimit:
                    raise RateLimit
                except FileError as e:
                    logging.exception(
                        f"Error in function '{func.__name__}': {type(e).__name__}:"
                    )
                    raise FileError(e)
                except RequestError as e:
                    logging.exception(
                        f"Error in function '{func.__name__}': {type(e).__name__}:"
                    )
                    raise RequestError(f"{e} \nThis usually means the file is broken.")
                except Exception as e:
                    last_exception = e
                    if retries == max_retries:
                        logging.exception(
                            f"Error in function '{func.__name__}': {type(e).__name__}:"
                        )
                        break
                    wait_time = backoff_factor**retries
                    logging.warning(
                        f"⚠️ Exception in function '{func.__name__}': {type(e).__name__} - {e}"
                    )
                    logging.warning(f"⌛ Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                    retries += 1
            raise last_exception

        return wrapper

    return decorator


def nomal_retry(max_retries=3, backoff_factor=2):
    """
    Decorator to retry an async function when an exception is raised.
    `max_retries`: Maximum number of retries.
    `backoff_factor`: Factor to increase the wait time between retries.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries + 1:
                try:
                    return func(*args, **kwargs)
                except RateLimit:
                    raise RateLimit
                except FileError as e:
                    logging.exception(
                        f"Error in function '{func.__name__}': {type(e).__name__}:"
                    )
                    raise e
                except Exception as e:
                    last_exception = e
                    if retries == max_retries:
                        logging.exception(
                            f"Error in function '{func.__name__}': {type(e).__name__}:"
                        )
                        break
                    wait_time = backoff_factor**retries
                    logging.warning(
                        f"⚠️ Exception in function '{func.__name__}': {type(e).__name__} - {e}"
                    )
                    logging.warning(f"⌛ Retrying in {wait_time} seconds.")
                    time.sleep(wait_time)
                    retries += 1
            raise last_exception

        return wrapper

    return decorator


def run_async(coro):
    """This function is used to run async function in sync way. As `asyncio.run` not work in jupyter notebook.

    Args:
        coro (_type_): The function to run.

    Returns:
        _type_: The result of the function.
    """
    if "IPython" in sys.modules:
        # Jupyter Notebook
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
    # Python
    return asyncio.run(coro)
