import logging
from fastapi import FastAPI, Request
import time
from functools import wraps

logger = logging.getLogger("uvicorn")

def log_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"Finished {func.__name__} in {end_time - start_time:.2f}s")
        return result
    return wrapper

async def log_request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "")
    start_time = time.time()
    
    logger.info(f"Request started - ID: {request_id} - Method: {request.method} - Path: {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Request completed - ID: {request_id} - Method: {request.method} - "
            f"Path: {request.url.path} - Status: {response.status_code} - "
            f"Time: {process_time:.2f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed - ID: {request_id} - Method: {request.method} - "
            f"Path: {request.url.path} - Time: {process_time:.2f}s - Error: {str(e)}"
        )
        raise

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await log_request_middleware(request, call_next)