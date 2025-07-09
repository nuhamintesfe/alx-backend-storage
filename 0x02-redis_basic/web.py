#!/usr/bin/env python3
"""
Implements a web cache using Redis with expiration and access counting.
"""

import redis
import requests
from typing import Optional


def get_page(url: str) -> Optional[str]:
    """
    Requests the HTML of a URL, caches it for 10 seconds, 
    and counts access using Redis.
    """
    r = redis.Redis()
    key = f"cache:{url}"
    count_key = f"count:{url}"

    # Increment access counter
    r.incr(count_key)

    # Return cached response if exists
    page = r.get(key)
    if page:
        return page.decode('utf-8')

    # Otherwise fetch, cache, and return
    response = requests.get(url)
    if response.status_code != 200:
        return None

    content = response.text
    r.setex(key, 10, content)
    return content
