from functools import wraps
from typing import Callable


def singleton(cls: type) -> Callable:
    instance = None

    @wraps(cls)
    def get_singleton_class(*args, **kwargs) -> object:
        nonlocal instance
        if not instance:
            instance = cls(*args, **kwargs)
        return instance
    return get_singleton_class
