#!/usr/bin/env python3
"""Redis basic cache exercise with call counting and history replay."""

from typing import Callable, Optional, Union
import redis
import uuid
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count calls of a method using Redis."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs for a method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        in_key = method.__qualname__ + ":inputs"
        out_key = method.__qualname__ + ":outputs"
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, result)
        return result
    return wrapper


def replay(fn: Callable):
    """Display the history of calls of a particular function."""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return

    fxn_name = fn.__qualname__
    in_key = fxn_name + ":inputs"
    out_key = fxn_name + ":outputs"

    count = 0
    if redis_store.exists(fxn_name):
        count = int(redis_store.get(fxn_name))

    print(f"{fxn_name} was called {count} times:")

    inputs = redis_store.lrange(in_key, 0, -1)
    outputs = redis_store.lrange(out_key, 0, -1)

    for i, o in zip(inputs, outputs):
        print(f"{fxn_name}(*{i.decode('utf-8')}) -> {o}")


class Cache:
    """Cache class for storing data in Redis."""

    def __init__(self):
        """Initialize Redis client and flush database synchronously."""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data with a random key in Redis and return the key.

        Args:
            data: Data to store (str, bytes, int, float).

        Returns:
            The key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Optional[Union[str, bytes, int, float]]:
        """
        Retrieve data by key and optionally convert it using a function.

        Args:
            key: The key string.
            fn: Optional callable to convert the data.

        Returns:
            The retrieved and optionally converted data, or None.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

        def get_str(self, key: str) -> Optional[str]:
            """
        Retrieve data as string.

        Args:
            key: The key string.

        Returns:
            The data decoded as UTF-8 string, or None.
           """
        return self.get(
            key,
            lambda d: d.decode('utf-8')
        )

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve data as integer.

        Args:
            key: The key string.

        Returns:
            The data converted to int, or None.
        """
        return self.get(key, lambda d: int(d))


if __name__ == "__main__":
    cache = Cache()

    key1 = cache.store("foo")
    key2 = cache.store("bar")
    key3 = cache.store(42)

    replay(cache.store)
