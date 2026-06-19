"""借还订单模型：关联用户与设备，记录幂等键与使用费用。"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BorrowOrder(Base):
  __tablename__ = "borrow_orders"

  id: Mapped[str] = mapped_column(
    CHAR(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
  )
  user_id: Mapped[str] = mapped_column(
    CHAR(36),
    ForeignKey("users.id"),
    nullable=False,
    index=True,
  )
  device_id: Mapped[str] = mapped_column(
    CHAR(36),
    ForeignKey("devices.id"),
    nullable=False,
    index=True,
  )
  status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
  borrowed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  due_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
  returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  usage_fee: Mapped[Decimal] = mapped_column(
    Numeric(12, 2),
    nullable=False,
    default=Decimal("0.00"),
    server_default="0.00",
  )
  idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
  return_idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
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
