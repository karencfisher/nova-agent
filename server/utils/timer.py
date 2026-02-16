import time


def timer(func):
    def wrapper_func(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f'{func} took {elapsed_time} seconds')
        return result
    return wrapper_func
