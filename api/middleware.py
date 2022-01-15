import imp
import logging
import time

from fastapi import Request

from api.Config import app

logger = logging.getLogger(__name__)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    url = request.url.remove_query_params('token')._url
    logger.debug(f'{url=};{process_time=}')
    return response
