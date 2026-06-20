"""借还订单服务。"""

import math
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.db.models.borrow_order import BorrowOrder
from app.db.models.device import Device
from app.db.models.user import User
from app.services.deposits import freeze_deposit, refund_deposit
from app.services.devices import get_device_by_code
from app.core.lock import redis_lock


def create_borrow_order(
    db: Session,
    user: User,
    *,
    device_code: str,
    idempotency_key: str,
) -> tuple[BorrowOrder, Device, Decimal]:
    """创建借出订单。

    返回 (order, device, deposit_frozen)。
    """
    existing = db.execute(
        select(BorrowOrder).where(BorrowOrder.idempotency_key == idempotency_key)
    ).scalar_one_or_none()
    if existing:
        raise ValueError("该请求已处理，请勿重复提交")

    active_order = db.execute(
        select(BorrowOrder).where(
            and_(
                BorrowOrder.user_id == user.id,
                BorrowOrder.status.in_(["active", "overdue"]),
            )
        )
    ).scalar_one_or_none()
    if active_order:
        raise ValueError("你已有未归还的设备，请先归还后再借新设备")

    if user.status == "blocked":
        raise ValueError("账号已被限制，无法借出设备")

    with redis_lock(f"device:{device_code}", timeout=10):
        device = get_device_by_code(db, device_code)
        if not device:
            raise ValueError("设备不存在")
        if device.status != "available":
            raise ValueError(f"设备当前不可借用（状态: {device.status}）")

        required_deposit = device.deposit_amount
        if user.deposit_balance < required_deposit:
            raise ValueError(
                f"押金余额不足，需要 {required_deposit}，当前 {user.deposit_balance}"
            )

        now = datetime.utcnow()
        due_at = now + timedelta(minutes=device.free_minutes)

        order = BorrowOrder(
            user_id=user.id,
            device_id=device.id,
            status="active",
            borrowed_at=now,
            due_at=due_at,
            idempotency_key=idempotency_key,
        )
        db.add(order)
        freeze_deposit(db, user, required_deposit, order.id)
        device.status = "borrowed"
        db.commit()
        db.refresh(order)
        return order, device, required_deposit


def return_borrow_order(
    db: Session,
    order: BorrowOrder,
    *,
    idempotency_key: str,
) -> dict:
    """归还借出订单。"""
    with redis_lock(f"order:{order.id}", timeout=10):
        if order.status not in ("active", "overdue"):
            raise ValueError(f"订单状态为 {order.status}，无法归还")
        if order.return_idempotency_key == idempotency_key:
            raise ValueError("该归还请求已处理，请勿重复提交")
        existing = db.execute(
            select(BorrowOrder).where(
                BorrowOrder.return_idempotency_key == idempotency_key,
                BorrowOrder.id != order.id,
            )
        ).scalar_one_or_none()
        if existing:
            raise ValueError("该幂等键已被其他订单使用")

        now = datetime.utcnow()
        order.returned_at = now
        order.status = "returned"
        order.return_idempotency_key = idempotency_key

        device = db.get(Device, order.device_id)
        actual_seconds = (now - order.borrowed_at).total_seconds()
        actual_minutes = actual_seconds / 60
        free_minutes = device.free_minutes

        if actual_minutes <= free_minutes:
            usage_fee = Decimal("0.00")
        else:
            chargeable_minutes = actual_minutes - free_minutes
            overdue_hours = math.ceil(chargeable_minutes / 60)
            usage_fee = (device.hourly_rate * Decimal(str(overdue_hours))).quantize(Decimal("0.01"))

        total_fee = usage_fee
        order.overdue_fee = usage_fee

        frozen_deposit = device.deposit_amount
        refund_amount = (frozen_deposit - total_fee).quantize(Decimal("0.01"))
        if refund_amount < 0:
            refund_amount = Decimal("0.00")

        user = db.get(User, order.user_id)
        deduction = total_fee - refund_amount
        if deduction > 0:
            user.deposit_balance = max(Decimal("0.00"), user.deposit_balance - deduction)
            if user.deposit_balance <= 0 and usage_fee > 0:
                user.status = "blocked"

        refund_deposit(db, order.user_id, refund_amount, order.id, "归还退还")
        device.status = "available"

        db.commit()
        db.refresh(order)

        return {
            "id": str(order.id),
            "returned_at": now,
            "actual_hours": round(actual_minutes / 60, 2),
            "usage_fee": usage_fee,
            "total_fee": total_fee,
            "deposit_refund": refund_amount,
        }


def get_user_current_order(db: Session, user: User) -> BorrowOrder | None:
    stmt = select(BorrowOrder).where(
        and_(
            BorrowOrder.user_id == user.id,
            BorrowOrder.status.in_(["active", "overdue"]),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_user_orders(
    db: Session,
    user: User,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BorrowOrder], int]:
    stmt = select(BorrowOrder).where(BorrowOrder.user_id == user.id)
    if status:
        stmt = stmt.where(BorrowOrder.status == status)
    count_stmt = select(BorrowOrder).where(BorrowOrder.user_id == user.id)
    if status:
        count_stmt = count_stmt.where(BorrowOrder.status == status)
    total = len(db.execute(count_stmt).scalars().all())
    stmt = stmt.order_by(BorrowOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars().all())
    return items, total
