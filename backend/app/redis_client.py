import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Note regarding decode_responses: we're storing strings/JSON directly.
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_cached_data(key: str):
    """Retrieve data from Redis if it exists."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except redis.RedisError:
        pass  # Silently fail if Redis is unavailable during dev
    return None

def set_cached_data(key: str, data: dict, expire: int = 3600):
    """Store data inside Redis with TTL (default 1 hr)."""
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except redis.RedisError:
        pass
