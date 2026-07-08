"""用户模型：手机号登录、押金余额与账号状态。"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[str] = mapped_column(
    CHAR(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
  )
  phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
  nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
  student_id: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)
  name: Mapped[str | None] = mapped_column(String(50), nullable=True)
  deposit_balance: Mapped[Decimal] = mapped_column(
    Numeric(12, 2),
    nullable=False,
    default=Decimal("0.00"),
    server_default="0.00",
  )
  role: Mapped[str] = mapped_column(String(16), nullable=False, default="user", server_default="user")
  status: Mapped[str] = mapped_column(
    String(16),
    nullable=False,
    default="active",
    server_default="active",
    index=True,
  )
  created_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.now(),
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.now(),
    onupdate=func.now(),
  )
