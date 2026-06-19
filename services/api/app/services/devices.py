"""设备服务。"""

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.device import Device
from app.db.models.borrow_order import BorrowOrder


def get_device_by_code(db: Session, device_code: str) -> Device | None:
    """按 device_code 查找设备。"""
    stmt = select(Device).where(Device.device_code == device_code)
    return db.execute(stmt).scalar_one_or_none()


def get_device_by_id(db: Session, device_id: str) -> Device | None:
    """按 ID 查找设备。"""
    return db.get(Device, device_id)


def list_devices(
    db: Session,
    *,
    category: str | None = None,
    status: str | None = None,
    location: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Device], int]:
    """分页查询设备列表。"""
    stmt = select(Device)
    if category:
        stmt = stmt.where(Device.category == category)
    if status:
        stmt = stmt.where(Device.status == status)
    if location:
        stmt = stmt.where(Device.location.ilike(f"%{location}%"))

    # 总数
    count_stmt = select(Device)
    if category:
        count_stmt = count_stmt.where(Device.category == category)
    if status:
        count_stmt = count_stmt.where(Device.status == status)
    if location:
        count_stmt = count_stmt.where(Device.location.ilike(f"%{location}%"))

    total = len(db.execute(count_stmt).scalars().all())

    stmt = stmt.order_by(Device.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def create_device(
    db: Session,
    *,
    device_code: str,
    name: str,
    hourly_rate: Decimal,
    category: str | None = None,
    location: str | None = None,
) -> Device:
    """创建设备。"""
    device = Device(
        device_code=device_code,
        name=name,
        hourly_rate=hourly_rate,
        category=category,
        location=location,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device: Device, updates: dict[str, Any]) -> Device:
    """更新设备字段。"""
    for key, value in updates.items():
        if value is not None:
            setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    """删除设备（需无活跃订单）。"""
    active_stmt = select(BorrowOrder).where(
        BorrowOrder.device_id == device.id,
        BorrowOrder.status == "active",
    )
    active = db.execute(active_stmt).scalar_one_or_none()
    if active:
        raise ValueError("设备存在活跃订单，无法删除")
    db.delete(device)
    db.commit()
