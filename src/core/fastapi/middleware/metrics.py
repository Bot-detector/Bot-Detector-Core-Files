from prometheus_client.metrics import Counter, Histogram

import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "request_count", "Total number of requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of requests in seconds", ["method", "endpoint"]
)


# Middleware for Prometheus metrics logging
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()

        # Start timer for request latency
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate request latency
        latency = time.perf_counter() - start_time

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(latency)

        return response