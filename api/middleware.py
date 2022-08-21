import json
import logging
import time

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.Config import app

logger = logging.getLogger(__name__)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    url = request.url.remove_query_params("token")._url
    logger.debug({"url": url, "process_time": process_time})
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = json.loads(exc.json())
    logger.warning({
        "url_path": request.url.path,
        "method": request.method,
        "path_params": request.path_params,
        "query_params": request.query_params,
        "error": error
    })
    return JSONResponse(content={"detail": error}, status_code=422)
