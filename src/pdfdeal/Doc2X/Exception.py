import asyncio
from functools import wraps
import time
from collections import deque


class RateLimit(Exception):
    """
    Error when rate limit is reached.
    """

    pass


class FileError(Exception):
    """
    Error when file is not found or cannot be opened or othes.
    """

    pass


def async_retry(max_retries=3, backoff_factor=2):
    """
    Decorator to retry an async function when an exception is raised.
    `max_retries`: Maximum number of retries.
    `backoff_factor`: Factor to increase the wait time between retries.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except RateLimit:
                    raise RateLimit
                except FileError as e:
                    raise e
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor**retries
                    print(
                        f"Failed to connect to the server. Retrying in {wait_time} seconds."
                    )
                    await asyncio.sleep(wait_time)
                    retries += 1
            raise last_exception

        return wrapper

    return decorator


class RateLimiter:
    def __init__(self, rpm):
        self.rpm = rpm
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.semaphore = asyncio.Semaphore(rpm)
        self.last_call_times = deque(maxlen=rpm)
        self.lock = asyncio.Lock()

    async def require(self):
        async with self.semaphore:
            async with self.lock:
                now = time.time()
                if len(self.last_call_times) >= self.rpm:
                    elapsed_time = now - self.last_call_times[-1]
                    if elapsed_time < 60:
                        wait_time = 60 - elapsed_time + 5
                        await asyncio.sleep(wait_time)
                self.last_call_times.append(now)

    async def release(self):
        self.semaphore.release()
