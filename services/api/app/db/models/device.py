"""设备模型：二维码业务码、位置、押金、免费分钟与小时单价。"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Device(Base):
  __tablename__ = "devices"

  id: Mapped[str] = mapped_column(
    CHAR(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
  )
  device_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(128), nullable=False)
  category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
  location: Mapped[str | None] = mapped_column(String(256), nullable=True)
  hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
  deposit_amount: Mapped[Decimal] = mapped_column(
    Numeric(12, 2),
    nullable=False,
    default=Decimal("0.00"),
    server_default="0.00",
  )
  free_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5, server_default="5")
  status: Mapped[str] = mapped_column(
    String(16),
    nullable=False,
    default="available",
    server_default="available",
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
