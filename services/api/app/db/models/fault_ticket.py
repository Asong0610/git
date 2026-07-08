"""故障报修工单模型：用户提交设备故障，管理员跟进处理。"""

import uuid
from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FaultRepairTicket(Base):
    __tablename__ = "fault_repair_tickets"

    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    device_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("devices.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    admin_remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
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