"""应用配置：从环境变量读取数据库、Redis 等连接信息。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=("deploy/.env", ".env"),
    env_file_encoding="utf-8",
    extra="ignore",
  )

  database_url: str = "mysql+pymysql://campus:campus@127.0.0.1:3306/campus_device"
  redis_url: str = "redis://127.0.0.1:6379/0"
  jwt_secret: str = "change-me-in-production"
  jwt_access_expire_minutes: int = 60
  jwt_refresh_expire_days: int = 7
  app_env: str = "development"
  app_debug: bool = True


@lru_cache
def get_settings() -> Settings:
  return Settings()
