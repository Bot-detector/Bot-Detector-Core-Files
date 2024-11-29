import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        query_params_list = [
            (key, value if key != "token" else "***")
            for key, value in request.query_params.items()
        ]

        logger.info(
            {
                "url": request.url.path,
                "params": query_params_list,
                "process_time": f"{process_time:.4f}",
            }
        )
        return response