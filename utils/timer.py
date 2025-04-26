import time


def timer(func):
    def wrapper_func(*args):
        start_time = time.time()
        result = func(*args)
        elapsed_time = time.time() - start_time
        print(f'{func} took {elapsed_time} seconds')
        return result
    return wrapper_func
