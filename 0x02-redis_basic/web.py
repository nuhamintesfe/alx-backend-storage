#!/usr/bin/env python3
'''Module for caching web pages and tracking access counts using Redis.'''

import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()
'''Redis client instance shared by all functions in this module.'''


def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    '''Decorator to cache page content and track the number of accesses per URL.'''

    @wraps(method)
    def wrapper(url: str) -> str:
        '''Fetches cached page content if available, otherwise fetches from the URL,
        caches it for 10 seconds, and tracks access count.'''
        # Increment access count
        redis_store.incr(f'count:{url}')

        # Check cache
        cached_result = redis_store.get(f'result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')

        # Fetch fresh content
        result = method(url)

        # Cache content with 10 seconds expiration
        redis_store.setex(f'result:{url}', 10, result)

        return result

    return wrapper


@data_cacher
def get_page(url: str) -> str:
    '''Fetch the HTML content of a URL.'''

    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError if bad response
    return response.text
