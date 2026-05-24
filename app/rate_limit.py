import redis
from fastapi import Request, HTTPException, status

redis_client = redis.Redis(host="localhost", port = 6379, db = 0)

def rate_limit(limit: int  = 5, window: int = 60):
    def dependency(request: Request):
        ip = request.client.host
        key = f"rate_limit: {ip}: {request.url.path}"
        count = redis_client.get(key)

        if count is None:
            redis_client.set(key, 1, ex = window)

        elif int(count) < limit:
            redis_client.incr(key)

        else:
            ttl = redis_client.ttl(key)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail = f"Too many requests. Please try again in {ttl} seconds.")
        
    return dependency
        
