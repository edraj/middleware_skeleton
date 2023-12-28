#!/usr/bin/env -S BACKEND_ENV=config.env python3
""" FastApi Main module """

import asyncio
import json
import sys
import time
import traceback
from datetime import datetime
from typing import Any
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.exceptions import HTTPException as StarletteHTTPException
from urllib.parse import quote
from utils.logger import logging_schema
from pydantic import ValidationError
from contextlib import asynccontextmanager
from api.order.router import router as orderRouter

from api.schemas.response import ApiException, ApiResponse, Error
from models.base.enums import Status

from utils.response import MainResponse
from fastapi.logger import logger
from utils.settings import settings
import socket
import subprocess
from api.auth.router import router as auth
from api.user.router import router as user_routers

service_start_time: str = ""
version: str = "unknown"
branch_name: str = "unknown"
server_hostname: str = "unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('{"stage":"starting up"}')
    logger.info("Starting up")
    global service_start_time
    global version
    global branch_name
    global server_hostname
    service_start_time = datetime.now().isoformat()
    branch_name_cmd = "git rev-parse --abbrev-ref HEAD"
    result = subprocess.run(
        [branch_name_cmd], capture_output=True, text=True, shell=True
    )
    branch_name = result.stdout.split("\n")[0]
    git_hash_cmd = "git rev-parse --short HEAD"
    result = subprocess.run([git_hash_cmd], capture_output=True, text=True, shell=True)
    version = result.stdout.split("\n")[0]
    server_hostname = socket.gethostname()

    openapi_schema = app.openapi()
    paths = openapi_schema["paths"]
    for path in paths:
        for method in paths[path]:
            responses = paths[path][method]["responses"]
            if responses.get("422"):
                responses.pop("422")
    app.openapi_schema = openapi_schema

    yield

    logger.info("Application shutting down")
    print('{"stage":"shutting down"}')


app = FastAPI(
    lifespan=lifespan,
    title="Middleware API",
    description="""Middleware uservice""",
    default_response_class=MainResponse,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    version="0.0.1",
    redoc_url=None,
    docs_url=f"{settings.base_path}/docs",
    openapi_url=f"{settings.base_path}/openapi.json",
    servers=[{"url": f"{settings.base_path}/"}],
)


async def capture_body(request: Request):
    request.state.request_body = {}
    if (
        request.method == "POST"
        and request.headers.get("content-type") == "application/json"
    ):
        request.state.request_body = await request.json()


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(_, exception):
    return MainResponse(
        content=exception.detail,
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    err = jsonable_encoder({"detail": exc.errors()})["detail"]
    raise ApiException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=Error(code=422, type="validation", message=err),
    )


@app.middleware("http")
async def middle(request: Request, call_next):
    """Wrapper function to manage errors and logging"""
    if request.url._url.endswith("/docs") or request.url._url.endswith("/openapi.json"):
        return await call_next(request)

    start_time = time.time()
    response_body: str = ""
    exception_data: dict[str, Any] | None = None
    # The api_key is enforced only if it set to none-empty value
    if not settings.api_key or (
        "key" in request.query_params
        and settings.api_key == request.query_params["key"]
    ):
        try:
            response = await call_next(request)
            response.headers["path"] = request.url.path

        except ApiException as ex:
            response = JSONResponse(
                status_code=ex.status_code,
                content=jsonable_encoder(
                    ApiResponse(status=Status.failed, error=ex.error)
                ),
            )
            stack = [
                {
                    "file": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line": lineno,
                }
                for frame, lineno in traceback.walk_tb(ex.__traceback__)
                if "site-packages" not in frame.f_code.co_filename
            ]
            exception_data = {"props": {"exception": str(ex), "stack": stack}}
            response_body = json.loads(response.body.decode())
        except ValidationError as e:
            stack = [
                {
                    "file": frame.f_code.co_filename,
                    "function": frame.f_code.co_name,
                    "line": lineno,
                }
                for frame, lineno in traceback.walk_tb(e.__traceback__)
                if "site-packages" not in frame.f_code.co_filename
            ]
            exception_data = {"props": {"exception": str(e), "stack": stack}}
            response = JSONResponse(
                status_code=422,
                content={
                    "status": "failed",
                    "error": {
                        "code": 422,
                        "type": "validation",
                        "message": "Validation error [2]",
                        "info": e.errors(),
                    },
                },
            )
            response_body = json.loads(response.body.decode())
        except Exception:
            exception_message = ""
            stack = None
            if ee := sys.exc_info()[1]:
                stack = [
                    {
                        "file": frame.f_code.co_filename,
                        "function": frame.f_code.co_name,
                        "line": lineno,
                    }
                    for frame, lineno in traceback.walk_tb(ee.__traceback__)
                    if "site-packages" not in frame.f_code.co_filename
                ]
                exception_message = str(ee)
                exception_data = {"props": {"exception": str(ee), "stack": stack}}

            error_log = {"code": 99, "message": exception_message}
            if settings.debug_enabled:
                error_log["stack"] = stack
            response = JSONResponse(
                status_code=500,
                content={
                    "status": "failed",
                    "error": error_log,
                },
            )
            response_body = json.loads(response.body.decode())
            logger.error("INTERNAL ERROR", extra={"props": exception_data})

    else:
        response = MainResponse(
            headers={
                "path": request.url.path,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ApiResponse(
                    status=Status.failed,
                    error=Error(type="bad_request", code=112, message="bad_request."),
                )
            ),
        )
        response_body = json.loads(response.body.decode())

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Server-Time"] = datetime.now().isoformat()
    extra = {
        "props": {
            "duration": 1000 * (time.time() - start_time),
            "request": {
                "verb": request.method,
                "path": quote(str(request.url.path)),
                "headers": dict(request.headers.items()),
                "query_params": dict(request.query_params.items()),
                "body": request.state.request_body
                if hasattr(request.state, "request_body")
                else {},
            },
            "response": {
                "headers": dict(response.headers.items()),
                "body": response_body,
            },
            "http_status": response.status_code,
        }
    }

    if exception_data is not None:
        extra["props"]["exception"] = exception_data
    if hasattr(request.state, "request_body"):
        extra["props"]["request"]["body"] = request.state.request_body
    if response_body:
        extra["props"]["response"]["body"] = response_body

    request.state.extra = extra
    if not response.status_code == 200:
        logger.info("Processed", extra=extra)
    return response


@app.get("/", include_in_schema=False, dependencies=[Depends(capture_body)])
async def root():
    """Micro-service card identifier"""

    return {
        "name": "DMW",
        "type": "microservice",
        "description": "Dmart Middleware",
        "status": "success",
        "start_time": service_start_time,
        "current_time": datetime.now(),
        "version": version,
        "branch_name": branch_name,
        "server": server_hostname,
    }


app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Correlation-ID",
    update_request_header=False,
)


app.include_router(
    auth, prefix="/auth", tags=["auth"], dependencies=[Depends(capture_body)]
)

app.include_router(
    user_routers, prefix="/user", tags=["user"], dependencies=[Depends(capture_body)]
)

app.include_router(
    orderRouter, prefix="/order", tags=["order"], dependencies=[Depends(capture_body)]
)


@app.options("/{x:path}", include_in_schema=False)
async def myoptions():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.post("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.put("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.patch("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
@app.delete("/{x:path}", include_in_schema=False, dependencies=[Depends(capture_body)])
async def catchall():
    raise ApiException(
        status_code=status.HTTP_404_NOT_FOUND,
        error=Error(
            type="catchall", code=230, message="Requested method or path is invalid"
        ),
    )


async def main():
    config = Config()
    config.bind = [f"{settings.listening_host}:{settings.listening_port}"]
    config.backlog = 200

    config.logconfig_dict = logging_schema
    config.errorlog = logger
    await serve(app, config)  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
