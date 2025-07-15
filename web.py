#!/usr/bin/env python3
"""Module for caching web pages and tracking access counts using Redis."""

import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()


def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    """Decorator to cache page content and track number of accesses."""

    @wraps(method)
    def wrapper(url: str) -> str:
        """Returns cached content if available, else fetches and caches."""
        redis_store.incr(f"count:{url}")

        cached_page = redis_store.get(f"cached:{url}")
        if cached_page:
            return cached_page.decode("utf-8")

        result = method(url)
        redis_store.setex(f"cached:{url}", 10, result)
        return result

    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL."""
    response = requests.get(url)
    return response.text
