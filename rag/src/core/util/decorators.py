import time
from functools import wraps


def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(f"Error occurred: {e}. Retrying {retries}/{max_retries}...")
                    if retries < max_retries:
                        time.sleep(delay)
                    else:
                        raise  # 如果重试次数用完，抛出异常

        return wrapper

    return decorator
