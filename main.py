#!/usr/bin/env -S BACKEND_ENV=config.env python3
""" Main module """
from starlette.datastructures import UploadFile
from contextlib import asynccontextmanager
import asyncio
import json
from os import getpid
import sys
import time
import traceback
from datetime import datetime
from typing import Any
from urllib.parse import urlparse, quote
from jsonschema.exceptions import ValidationError as SchemaValidationError
from pydantic import ValidationError

from utils.dmart import dmart
from utils.git_info import git_info
from utils.middleware import CustomRequestMiddleware, ChannelMiddleware
from utils.jwt import JWTBearer
from fastapi import Depends, FastAPI, Request, Response, status
from utils.logger import logging_schema
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.concurrency import iterate_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.settings import settings
from asgi_correlation_id import CorrelationIdMiddleware
from utils.internal_error_code import InternalErrorCode
import json_logging
from api.dummy.router import router as dummy_router
from pydmart.models import DmartException, Error as DmartError, ApiResponse, ApiResponseRecord
from pydmart.enums import ResourceType, Status as DmartStatus, Status


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up")
    print('{"stage":"starting up"}')

    try:
        r = await dmart.login(settings.dmart_username, settings.dmart_password)
        if r.status == Status.failed:
            sys.exit("Failed to connect to DMART")
    except Exception:
        sys.exit("Failed to connect to DMART")

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


json_logging.init_fastapi(enable_json=True)
app = FastAPI(
    lifespan=lifespan,
    title="Datamart API",
    description="Structured Content Management System",
    version=str(git_info()["tag"]),
    redoc_url=None,
    docs_url=f"{settings.base_path}/docs",
    openapi_url=f"{settings.base_path}/openapi.json",
    servers=[{"url": f"{settings.base_path}/"}],
    contact={
        "name": "Kefah T. Issa",
        "url": "https://dmart.cc",
        "email": "kefah.issa@gmail.com",
    },
    license_info={
        "name": "GNU Affero General Public License v3+",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=[],
)


async def capture_body(request: Request):
    request.state.request_body = {}

    if (
            request.method == "POST"
            and "application/json" in request.headers.get("content-type", "")
    ):
        request.state.request_body = await request.json()

    if (
            request.method == "POST"
            and request.headers.get("content-type")
            and "multipart/form-data" in request.headers.get("content-type", [])
    ):
        form = await request.form()
        for field in form:
            one = form[field]
            if isinstance(one, str):
                request.state.request_body[field] = form.get(field)
            elif isinstance(one, UploadFile):
                request.state.request_body[field] = {
                    "name": one.filename,
                    "content_type": one.content_type,
                }


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(_, exception):
    return JSONResponse(
        content=exception.detail,
        status_code=exception.status_code,
        headers={"correlation_id": json_logging.get_correlation_id()},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    err = jsonable_encoder({"detail": exc.errors()})["detail"]
    raise DmartException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=DmartError(
            code=InternalErrorCode.UNPROCESSABLE_ENTITY, type="validation", message="Validation error [1]", info=err
        ),
    )


app.add_middleware(CustomRequestMiddleware)
app.add_middleware(ChannelMiddleware)


def set_middleware_extra(request, response, start_time, user_shortname, exception_data, response_body):
    extra = {
        "props": {
            "timestamp": start_time,
            "duration": 1000 * (time.time() - start_time),
            "server": settings.servername,
            "process_id": getpid(),
            "user_shortname": user_shortname,
            "request": {
                "url": request.url._url,
                "verb": request.method,
                "path": quote(str(request.url.path)),
                "query_params": dict(request.query_params.items()),
                "headers": dict(request.headers.items()),
            },
            "response": {
                "headers": dict(response.headers.items()),
                "http_status": response.status_code,
            },
        }
    }

    if exception_data is not None:
        extra["props"]["exception"] = exception_data
    if (hasattr(request.state, "request_body") and isinstance(extra, dict) and isinstance(extra["props"], dict)
            and isinstance(extra["props"]["request"], dict)):
        extra["props"]["request"]["body"] = request.state.request_body
    if (response_body and isinstance(extra, dict) and isinstance(extra["props"], dict)
            and isinstance(extra["props"]["response"], dict)):
        extra["props"]["response"]["body"] = response_body

    return extra


def set_middleware_response_headers(request, response):
    referer = request.headers.get(
        "referer",
        request.headers.get("origin",
                            request.headers.get("x-forwarded-proto", "http")
                            + "://"
                            + request.headers.get(
                                "x-forwarded-host", f"{settings.listening_host}:{settings.listening_port}"
                            )),
    )
    origin = urlparse(referer)
    response.headers[
        "Access-Control-Allow-Origin"
    ] = f"{origin.scheme}://{origin.netloc}"

    # if "localhost" in response.headers["Access-Control-Allow-Origin"]:
    #     response.headers["Access-Control-Allow-Origin"] = "*"

    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "content-type, charset, authorization, accept-language, content-length"
    response.headers["Access-Control-Max-Age"] = "600"
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "OPTIONS, DELETE, POST, GET, PATCH, PUT"

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["x-server-time"] = datetime.now().isoformat()
    response.headers["Access-Control-Expose-Headers"] = "x-server-time"
    return response


def mask_sensitive_data(data):
    if isinstance(data, dict):
        return {k: mask_sensitive_data(v) if k not in ['password', 'access_token', 'refresh_token', 'auth_token'] else '******' for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    elif isinstance(data, str) and 'auth_token' in data:
        return '******'
    return data


def set_logging(response, extra, request, exception_data):
    extra = mask_sensitive_data(extra)
    if 400 <= response.status_code < 500:
        logger.warning("Served request", extra=extra) # type: ignore
    elif response.status_code >= 500 or exception_data is not None:
        logger.error("Served request", extra=extra) # type: ignore
    elif request.method != "OPTIONS":  # Do not log OPTIONS request, to reduce excessive logging
        logger.info("Served request", extra=extra) # type: ignore


def set_stack(e):
    return [
        {
            "file": frame.f_code.co_filename,
            "function": frame.f_code.co_name,
            "line": lineno,
        }
        for frame, lineno in traceback.walk_tb(e.__traceback__)
        if "site-packages" not in frame.f_code.co_filename
    ]

@app.middleware("http")
async def middle(request: Request, call_next):
    """Wrapper function to manage errors and logging"""
    if request.url._url.endswith("/docs") or request.url._url.endswith("openapi.json"):
        return await call_next(request)

    start_time = time.time()
    response_body: str | dict = {}
    exception_data: dict[str, Any] | None = None

    try:
        response = await asyncio.wait_for(call_next(request), timeout=settings.request_timeout)
        response.headers["correlation_id"] = json_logging.get_correlation_id()
        raw_response = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(raw_response))
        raw_data = b"".join(raw_response)
        if raw_data:
            try:
                response_body = json.loads(raw_data)
            except Exception:
                response_body = {}
    except asyncio.TimeoutError:
        response = JSONResponse(content={'status':'failed',
            'error': {"code":504, "message": 'Request processing time exceeded limit'}},
            status_code=status.HTTP_504_GATEWAY_TIMEOUT)
        response_body = json.loads(str(response.body, 'utf8'))
    except DmartException as e:
        response = JSONResponse(
            headers={
                "correlation_id": json_logging.get_correlation_id(),
            },
            status_code=e.status_code,
            content=jsonable_encoder(
                ApiResponse(status=DmartStatus.failed, error=e.error, records=[])
            ),
        )
        stack = set_stack(e)
        exception_data = {"props": {"exception": str(e), "stack": stack}}
        response_body = json.loads(str(response.body, 'utf8'))
    except ValidationError as e:
        stack = set_stack(e)
        exception_data = {"props": {"exception": str(e), "stack": stack}}
        response = JSONResponse(
            headers={
                "correlation_id": json_logging.get_correlation_id(),
            },
            status_code=422,
            content={
                "status": "failed",
                "error": {
                    "type": "validation",
                    "code": 422,
                    "message": "Validation error [2]",
                    "info": jsonable_encoder(e.errors()),
                },
            },
        )
        response_body = json.loads(str(response.body, 'utf8'))
    except SchemaValidationError as e:
        stack = set_stack(e)
        exception_data = {"props": {"exception": str(e), "stack": stack}}
        response = JSONResponse(
            headers={
                "correlation_id": json_logging.get_correlation_id(),
            },
            status_code=400,
            content={
                "status": "failed",
                "error": {
                    "type": "validation",
                    "code": 422,
                    "message": "Validation error [3]",
                    "info": [{
                        "loc": list(e.path),
                        "msg": e.message
                    }],
                },
            },
        )
        response_body = json.loads(str(response.body, 'utf8'))
    except Exception as _:
        exception_message = ""
        stack = None
        if ee := sys.exc_info()[1]:
            stack = set_stack(ee)
            exception_message = str(ee)
            exception_data = {"props": {"exception": str(ee), "stack": stack}}

        error_log = {"type": "general", "code": 99, "message": exception_message}
        if settings.debug_enabled:
            error_log["stack"] = stack
        response = JSONResponse(
            headers={
                "correlation_id": json_logging.get_correlation_id(),
            },
            status_code=500,
            content={
                "status": "failed",
                "error": error_log,
            },
        )
        response_body = json.loads(str(response.body, 'utf8'))


    response = set_middleware_response_headers(request, response)

    user_shortname = "guest"
    try:
        user_shortname = str(await JWTBearer().__call__(request))
    except Exception:
        pass

    extra = set_middleware_extra(request, response, start_time, user_shortname, exception_data, response_body)

    set_logging(response, extra, request, exception_data)

    return response


app.add_middleware(
    CorrelationIdMiddleware,
    header_name='X-Correlation-ID',
    update_request_header=False,
    validator=None,
)


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "success", "message": "DMART Microservice API"}


@app.get("/spaces-backup", include_in_schema=False)
async def space_backup(key: str):
    if not key or key != "ABC":
        return ApiResponse(
            status=DmartStatus.failed,
            error=DmartError(type="git", code=InternalErrorCode.INVALID_APP_KEY, message="Api key is invalid"),
            records=[]
        )

    import subprocess

    cmd = "/usr/bin/bash -c 'cd .. && ./spaces-backup.sh'"

    result_stdout, result_stderr = subprocess.Popen(
        cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()
    attributes = {
        "stdout": result_stdout.decode().split("\n"),
        "stderr": result_stderr.decode().split("\n"),
    }
    return ApiResponse(status=DmartStatus.success, records=[ApiResponseRecord(attributes=attributes, subpath="", resource_type=ResourceType.content, shortname="")])


app.include_router(
    dummy_router, prefix="/dummy", tags=["dummy"], dependencies=[Depends(capture_body)]
)


@app.options("/{x:path}", include_in_schema=False)
async def myoptions():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/{x:path}", include_in_schema=False)
@app.post("/{x:path}", include_in_schema=False)
@app.put("/{x:path}", include_in_schema=False)
@app.patch("/{x:path}", include_in_schema=False)
@app.delete("/{x:path}", include_in_schema=False)
async def catchall() -> None:
    raise DmartException(
        status_code=status.HTTP_404_NOT_FOUND,
        error=DmartError(
            type="catchall", code=InternalErrorCode.INVALID_ROUTE, message="Requested method or path is invalid"
        ),
    )


json_logging.init_request_instrument(app)

async def main():
    config = Config()
    config.bind = [f"{settings.listening_host}:{settings.listening_port}"]
    config.backlog = 200

    config.logconfig_dict = logging_schema
    config.errorlog = logger

    try:
        await serve(app, config)  # type: ignore
    except OSError as e:
        print("[!1server]", e)


if __name__ == "__main__":
    asyncio.run(main())  # type: ignore

