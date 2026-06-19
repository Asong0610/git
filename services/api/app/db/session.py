"""数据库会话与引擎配置。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
  settings.database_url,
  pool_pre_ping=True,
  pool_recycle=3600,
  connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(
  bind=engine,
  autocommit=False,
  autoflush=False,
  expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
  """FastAPI 依赖：提供请求级数据库会话。"""
  database_session = SessionLocal()
  try:
    yield database_session
  finally:
    database_session.close()
