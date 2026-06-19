"""借还路由：借出、归还、订单查询。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models.borrow_order import BorrowOrder
from app.db.models.device import Device
from app.dependencies import get_db
from app.dependencies import get_current_user
from app.db.models.user import User
from app.schemas.borrow import (
    BorrowCreateRequest,
    BorrowResponse,
    ReturnRequest,
    ReturnResponse,
    OrderListResponse,
    OrderItemResponse,
    BorrowResponse,
    OrderDetailResponse,
)
from app.services.borrows import create_borrow_order, return_borrow_order, get_user_orders, get_user_current_order
from app.services.devices import get_device_by_code

router = APIRouter(prefix="/borrows", tags=["借还"])


@router.post("", response_model=BorrowResponse)
def borrow_device(
    body: BorrowCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """借出设备（扫码借用）。"""
    order, device, deposit_frozen = create_borrow_order(
        db,
        user,
        device_code=body.device_code,
        idempotency_key=body.idempotency_key,
    )

    return BorrowResponse(
        id=str(order.id),
        device_code=device.device_code,
        device_name=device.name,
        borrowed_at=order.borrowed_at,
        due_at=order.due_at,
        deposit_frozen=deposit_frozen,
    )


@router.post("/{order_id}/return", response_model=ReturnResponse)
def return_device(
    order_id: str,
    body: ReturnRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """归还设备。"""
    order = db.get(BorrowOrder, order_id)
    if not order:
        from app.core.exceptions import AppError
        raise AppError("订单不存在", code="ORDER_NOT_FOUND", status_code=404)
    if order.user_id != user.id:
        from app.core.exceptions import AppError
        raise AppError("无权操作此订单", code="FORBIDDEN", status_code=403)

    result = return_borrow_order(db, order, idempotency_key=body.idempotency_key)
    return ReturnResponse(**result)



@router.get("/current", response_model=BorrowResponse | None)
def get_current_order(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前进行中的订单（active）。"""
    order = get_user_current_order(db, user)
    if not order:
        return None

    device = db.get(Device, order.device_id)
    borrowed_hours = (order.due_at - order.borrowed_at).total_seconds() / 3600
    from decimal import Decimal
    frozen = device.hourly_rate * Decimal(str(borrowed_hours)) * 2 if device else Decimal("0.00")

    return BorrowResponse(
        id=str(order.id),
        device_code=device.device_code if device else "",
        device_name=device.name if device else "",
        borrowed_at=order.borrowed_at,
        due_at=order.due_at,
        deposit_frozen=frozen,
    )

@router.get("", response_model=OrderListResponse)
def list_orders(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询用户订单列表。"""
    items, total = get_user_orders(db, user, status=status, page=page, page_size=page_size)

    order_items = []
    for order in items:
        device = db.get(Device, order.device_id)
        order_items.append(
            OrderItemResponse(
                id=str(order.id),
                device_code=device.device_code if device else "",
                device_name=device.name if device else "",
                status=order.status,
                borrowed_at=order.borrowed_at,
                due_at=order.due_at,
                returned_at=order.returned_at,
                usage_fee=order.usage_fee,
            )
        )

    return OrderListResponse(items=order_items, total=total)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询订单详情。"""
    order = db.get(BorrowOrder, order_id)
    if not order:
        from app.core.exceptions import AppError
        raise AppError("订单不存在", code="ORDER_NOT_FOUND", status_code=404)
    if order.user_id != user.id:
        from app.core.exceptions import AppError
        raise AppError("无权查看此订单", code="FORBIDDEN", status_code=403)

    device = db.get(Device, order.device_id)
    return OrderDetailResponse(
        id=str(order.id),
        device_code=device.device_code if device else "",
        device_name=device.name if device else "",
        user_id=str(order.user_id),
        status=order.status,
        borrowed_at=order.borrowed_at,
        due_at=order.due_at,
        returned_at=order.returned_at,
        usage_fee=order.usage_fee,
    )
