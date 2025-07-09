# 0x02-redis_basic

## Overview

This project demonstrates basic Redis operations using Python, including:

- Storing arbitrary data types.
- Retrieving stored data with type preservation.
- Counting method calls.
- Logging input/output history of methods.
- Implementing a web cache with expiration and usage tracking.

## Files

### `exercise.py`

- Class `Cache` for storing and retrieving data.
- `store(data) -> key`: returns random key after storing.
- `get(key, fn=None)`: optional conversion via `fn`.
- `get_str(key)`, `get_int(key)`: convenience methods.
- Decorators:
  - `count_calls`: counts how many times `store` is called.
  - `call_history`: logs inputs & outputs for `store`.

### `web.py`

- Function `get_page(url) -> Optional[str]`: 
  - Counts accesses.
  - Caches content for 10 seconds.
  - Returns HTML content.

## Requirements

- Ubuntu 18.04, Python 3.7
- `redis-server` installed and bound to `127.0.0.1`
- Python dependencies: `redis`, `requests`
