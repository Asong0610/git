"""FastAPI 应用入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.json_encoder import custom_json_dumps

settings = get_settings()


class CustomJSONResponse(JSONResponse):
    """使用自定义编码器的 JSON 响应。"""

    def render(self, content) -> bytes:
        return custom_json_dumps(content).encode("utf-8")


app = FastAPI(
  title="校园共享设备借还 API",
  version="0.1.0",
  docs_url="/docs",
  redoc_url="/redoc",
  default_response_class=CustomJSONResponse,
)

register_exception_handlers(app)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
