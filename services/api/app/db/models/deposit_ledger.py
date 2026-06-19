"""押金流水模型：记录每笔押金变动及变动后余额。"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DepositLedger(Base):
  __tablename__ = "deposit_ledger"

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
  order_id: Mapped[str | None] = mapped_column(
    CHAR(36),
    ForeignKey("borrow_orders.id"),
    nullable=True,
  )
  entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
  amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
  balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
  remark: Mapped[str | None] = mapped_column(String(256), nullable=True)
  created_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.now(),
    index=True,
  )
