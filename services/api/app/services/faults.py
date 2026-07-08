"""故障报修工单服务层。"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models.device import Device
from app.db.models.fault_ticket import FaultRepairTicket
from app.db.models.user import User


ALLOWED_STATUSES = {"pending", "processing", "resolved", "closed"}


def create_fault_ticket(
    db: Session,
    user: User,
    device_id: str,
    description: str,
) -> FaultRepairTicket:
    """用户提交报修工单。"""
    device = db.get(Device, device_id)
    if not device:
        raise AppError("设备不存在", code="DEVICE_NOT_FOUND", status_code=404)

    ticket = FaultRepairTicket(
        device_id=device.id,
        user_id=user.id,
        description=description,
        status="pending",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_user_fault_tickets(
    db: Session,
    user: User,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[FaultRepairTicket], int]:
    """查询指定用户的报修记录（带 device_name / user_phone 预计算）。"""
    stmt = (
        select(FaultRepairTicket, Device.name.label("device_name"), User.phone.label("user_phone"))
        .join(Device, FaultRepairTicket.device_id == Device.id)
        .join(User, FaultRepairTicket.user_id == User.id)
        .where(FaultRepairTicket.user_id == user.id)
    )
    count_stmt = (
        select(FaultRepairTicket)
        .where(FaultRepairTicket.user_id == user.id)
    )

    total = db.execute(count_stmt).scalars().all().__len__()
    rows = db.execute(
        stmt.order_by(FaultRepairTicket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    for ticket, device_name, user_phone in rows:
        ticket.device_name = device_name
        ticket.user_phone = user_phone

    return [row[0] for row in rows], total


def get_fault_tickets(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
) -> tuple[list[FaultRepairTicket], int]:
    """管理端分页查询全部报修工单。"""
    stmt = (
        select(FaultRepairTicket, Device.name.label("device_name"), User.phone.label("user_phone"))
        .join(Device, FaultRepairTicket.device_id == Device.id)
        .join(User, FaultRepairTicket.user_id == User.id)
    )
    count_stmt = select(FaultRepairTicket)

    if status_filter:
        stmt = stmt.where(FaultRepairTicket.status == status_filter)
        count_stmt = count_stmt.where(FaultRepairTicket.status == status_filter)

    total = len(db.execute(count_stmt).scalars().all())
    rows = db.execute(
        stmt.order_by(FaultRepairTicket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    for ticket, device_name, user_phone in rows:
        ticket.device_name = device_name
        ticket.user_phone = user_phone

    return [row[0] for row in rows], total


def process_fault_ticket(
    db: Session,
    ticket_id: str,
    status: str,
    admin_remark: str | None,
) -> FaultRepairTicket:
    """管理员处理报修工单。"""
    if status not in ALLOWED_STATUSES:
        raise AppError("非法的工单状态", code="INVALID_STATUS", status_code=400)

    ticket = db.get(FaultRepairTicket, ticket_id)
    if not ticket:
        raise AppError("工单不存在", code="TICKET_NOT_FOUND", status_code=404)

    ticket.status = status
    if admin_remark is not None:
        ticket.admin_remark = admin_remark

    if status == "resolved":
        ticket.resolved_at = datetime.utcnow()
    elif status == "closed":
        # 关闭时若未设置解决时间，可置为当前时间（业务上关闭即完结）
        if not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    # 补齐关联信息
    device = db.get(Device, ticket.device_id)
    user = db.get(User, ticket.user_id)
    ticket.device_name = device.name if device else None
    ticket.user_phone = user.phone if user else None

    return ticket