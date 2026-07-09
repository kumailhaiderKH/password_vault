import redis
from fastapi import Request, HTTPException, status
from . import config

redis_client = redis.Redis(host="localhost", port = 6379, db = 0)

def rate_limit(limit: int = None, window: int = None):
    def dependency(request: Request):
        actual_limit = limit if limit is not None else config.settings.rate_limit_requests
        actual_window = window if window is not None else config.settings.rate_limit_window

        ip = request.client.host
        key = f"rate_limit:{ip}:{request.url.path}"
        count = redis_client.get(key)

        if count is None:
            redis_client.set(key, 1, ex = actual_window)

        elif int(count) < actual_limit:
            redis_client.incr(key)

        else:
            ttl = redis_client.ttl(key)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail = f"Too many requests. Please try again in {ttl} seconds.")
        
    return dependency
        
