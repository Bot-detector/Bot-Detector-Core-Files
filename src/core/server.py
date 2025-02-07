import json
import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import api
from starlette_prometheus import metrics, PrometheusMiddleware
from src.core.fastapi.middleware import LoggingMiddleware
logger = logging.getLogger(__name__)


def init_routers(_app: FastAPI) -> None:
    _app.include_router(api.router)


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "http://osrsbotdetector.com/",
                "https://osrsbotdetector.com/",
                "http://localhost",
                "http://localhost:8080",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(LoggingMiddleware)
    ]
    return middleware


def create_app() -> FastAPI:
    _app = FastAPI(
        title="Bot-Detector-API",
        description="Bot-Detector-API",
        middleware=make_middleware(),
    )
    init_routers(_app=_app)
    return _app


app = create_app()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/favicon")
async def favicon():
    return {}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = json.loads(exc.json())
    logger.warning(
        {
            "url_path": request.url.path,
            "method": request.method,
            "path_params": request.path_params,
            "query_params": request.query_params,
            "error": error,
        }
    )
    return JSONResponse(content={"detail": error}, status_code=422)