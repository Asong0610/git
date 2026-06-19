"""全局异常与统一错误响应格式。"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
  """业务层可抛出的应用异常。"""

  def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400):
    self.message = message
    self.code = code
    self.status_code = status_code
    super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
  @app.exception_handler(AppError)
  async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
      status_code=exc.status_code,
      content={"code": exc.code, "message": exc.message, "detail": None},
    )

  @app.exception_handler(StarletteHTTPException)
  async def handle_http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
      status_code=exc.status_code,
      content={
        "code": "HTTP_ERROR",
        "message": str(exc.detail),
        "detail": None,
      },
    )

  @app.exception_handler(ValueError)
  async def handle_value_error(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
      status_code=400,
      content={"code": "VALUE_ERROR", "message": str(exc), "detail": None},
    )

  @app.exception_handler(RequestValidationError)
  async def handle_validation_error(
    _request: Request,
    exc: RequestValidationError,
  ) -> JSONResponse:
    return JSONResponse(
      status_code=422,
      content={
        "code": "VALIDATION_ERROR",
        "message": "请求参数校验失败",
        "detail": exc.errors(),
      },
    )
