import redis

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_USERNAME
)


pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    username=REDIS_USERNAME,
    decode_responses=True,
    max_connections=20
)


r = redis.Redis(
    connection_pool=pool
)