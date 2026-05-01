from cachetools import TTLCache
from config.settings import CACHE_TTL

cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)

def get(key: str):
    return cache.get(key)

def set(key: str, value):
    cache[key] = value

def generate_key(query: str, num_results: int, mode: str, engines: list, time_range: str = "") -> str:
    data = f"{query}|{num_results}|{mode}|{','.join(engines or [])}|{time_range}"
    hash_val = hash(data)
    return f"search:{abs(hash_val)}"
