import asyncio
import functools
from utils.logger import logger

def async_retry(max_retries: int = 3, backoff_factor: float = 2.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            delay = 1.0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Error: {e}")
                        raise e
                    logger.warning(f"Retrying {func.__name__} in {delay:.1f}s due to: {e}")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
