import redis
import json
import os
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_cached_data(key: str):
    """Retrieve data from Redis if it exists."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except redis.RedisError as e:
        # FIX #14: Log the error instead of silently swallowing it.
        # A dead Redis is a real problem and should be visible in logs.
        logger.warning("Redis GET failed for key '%s': %s", key, e)
    return None

def set_cached_data(key: str, data: dict, expire: int = 3600):
    """Store data inside Redis with TTL (default 1 hr)."""
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except redis.RedisError as e:
        # FIX #14: Log instead of silently swallowing.
        logger.warning("Redis SET failed for key '%s': %s", key, e)
