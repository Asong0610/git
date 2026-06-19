"""健康检查接口：验证 API、PostgreSQL 与 Redis 连通性。"""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis import get_redis_client
from app.db.session import engine
from app.schemas.health import HealthResponse

router = APIRouter(tags=["健康检查"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
  database_status = "ok"
  redis_status = "ok"

  try:
    with engine.connect() as connection:
      connection.execute(text("SELECT 1"))
  except Exception:
    database_status = "error"

  try:
    redis_client = get_redis_client()
    if redis_client.ping() is not True:
      redis_status = "error"
  except Exception:
    redis_status = "error"

  overall_status = "ok" if database_status == "ok" and redis_status == "ok" else "degraded"

  return HealthResponse(
    status=overall_status,
    database=database_status,
    redis=redis_status,
  )
