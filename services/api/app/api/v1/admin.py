"""管理端路由：用户押金调账等。"""

from datetime import date
from decimal import Decimal
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.redis import get_redis_client
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import require_admin
from app.schemas.admin_user import FreezeRequest, UserItemResponse, UserListResponse
from app.schemas.deposit import DepositLedgerResponse
from app.schemas.fault import FaultListResponse, FaultProcessRequest, FaultItemResponse
from app.schemas.statistics import DeviceStatsItem, TimeStatsItem
from app.services.faults import get_fault_tickets, process_fault_ticket
from app.services.statistics import get_device_statistics, get_time_statistics, export_statistics_excel

router = APIRouter(prefix="/admin", tags=["管理端"])


class DepositAdjustRequest(BaseModel):
    amount: Decimal = Field(..., description="调整金额（正=充值，负=扣款）")
    remark: str = Field(default="管理员调账", max_length=256, description="备注")


@router.post("/users/{user_id}/deposit/adjust", response_model=DepositLedgerResponse)
def adjust_deposit(
    user_id: str,
    body: DepositAdjustRequest,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理员调账：充值或扣款用户押金。"""
    user = db.get(User, user_id)
    if not user:
        from app.core.exceptions import AppError
        raise AppError("用户不存在", code="USER_NOT_FOUND", status_code=404)

    # 扣款时余额不能为负
    if body.amount < 0 and user.deposit_balance + body.amount < 0:
        from app.core.exceptions import AppError
        raise AppError(
            f"扣款后余额将为负数，当前余额 {user.deposit_balance}，扣款 {abs(body.amount)}",
            code="INSUFFICIENT_BALANCE",
            status_code=400,
        )

    user.deposit_balance += body.amount

    # 如果被 blocked 且余额恢复到正数，自动解锁
    if user.status == "blocked" and user.deposit_balance > 0:
        user.status = "active"

    from app.db.models.deposit_ledger import DepositLedger
    ledger = DepositLedger(
        user_id=user.id,
        entry_type="adjust",
        amount=body.amount,
        balance_after=user.deposit_balance,
        remark=body.remark,
    )
    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return DepositLedgerResponse(
        id=str(ledger.id),
        entry_type=ledger.entry_type,
        amount=ledger.amount,
        balance_after=ledger.balance_after,
        remark=ledger.remark,
        created_at=ledger.created_at,
    )


@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query("", description="搜索关键字"),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """分页查询用户列表。"""
    query = db.query(User)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            or_(User.student_id.ilike(kw), User.name.ilike(kw), User.phone.ilike(kw))
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/users/{user_id}/freeze", response_model=UserItemResponse)
def freeze_user(
    user_id: str,
    body: FreezeRequest,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """冻结/解冻用户账号。"""
    user = db.get(User, user_id)
    if not user:
        raise AppError("用户不存在", code="USER_NOT_FOUND", status_code=404)

    if body.action == "freeze":
        user.status = "blocked"
    elif body.action == "unfreeze":
        user.status = "active"

    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-sms")
def reset_user_sms(
    user_id: str,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """重置用户短信验证码缓存。"""
    user = db.get(User, user_id)
    if not user:
        raise AppError("用户不存在", code="USER_NOT_FOUND", status_code=404)

    redis_client = get_redis_client()
    redis_client.delete(f"sms:{user.phone}")

    return {"message": "验证码已重置"}


@router.get("/users/export")
def export_users(
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """导出全部用户信息为 Excel。"""
    users = db.query(User).order_by(User.created_at.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "用户列表"
    ws.append(["学号", "姓名", "手机号", "押金余额", "注册时间", "账号状态"])

    for user in users:
        ws.append([
            user.student_id or "",
            user.name or "",
            user.phone,
            float(user.deposit_balance),
            user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "",
            "正常" if user.status == "active" else "冻结",
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"users_{date.today().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/faults", response_model=FaultListResponse)
def list_faults(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str | None = Query(None, description="工单状态筛选"),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """分页查询故障报修工单列表。"""
    items, total = get_fault_tickets(db, page=page, page_size=page_size, status_filter=status)
    return FaultListResponse(
        items=[FaultItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.put("/faults/{ticket_id}", response_model=FaultItemResponse)
def process_fault(
    ticket_id: str,
    body: FaultProcessRequest,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理员处理故障报修工单。"""
    ticket = process_fault_ticket(
        db,
        ticket_id,
        status=body.status,
        admin_remark=body.admin_remark,
    )
    return FaultItemResponse.model_validate(ticket)


@router.get("/statistics/orders", response_model=list[TimeStatsItem])
def statistics_orders(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    group_by: str = Query("day", description="分组维度: day/week/month"),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """按时间维度统计已归还订单。"""
    if start_date > end_date:
        raise AppError("开始日期不能大于结束日期", code="INVALID_DATE_RANGE", status_code=400)
    if group_by not in {"day", "week", "month"}:
        raise AppError("不支持的分组维度", code="INVALID_GROUP_BY", status_code=400)
    return get_time_statistics(db, start_date, end_date, group_by)


@router.get("/statistics/devices", response_model=list[DeviceStatsItem])
def statistics_devices(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """按设备维度统计已归还订单。"""
    if start_date > end_date:
        raise AppError("开始日期不能大于结束日期", code="INVALID_DATE_RANGE", status_code=400)
    return get_device_statistics(db, start_date, end_date)


@router.get("/statistics/export")
def statistics_export(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    group_by: str = Query("day", description="分组维度: day/week/month"),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """导出订单统计数据为 Excel。"""
    if start_date > end_date:
        raise AppError("开始日期不能大于结束日期", code="INVALID_DATE_RANGE", status_code=400)
    if group_by not in {"day", "week", "month"}:
        raise AppError("不支持的分组维度", code="INVALID_GROUP_BY", status_code=400)

    buffer = export_statistics_excel(db, start_date, end_date, group_by)
    filename = f"statistics_{start_date.isoformat()}_{end_date.isoformat()}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
