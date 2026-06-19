"""健康检查相关响应模型。"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
  status: str
  database: str
  redis: str
