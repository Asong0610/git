"""管理端路由：用户押金调账等。"""

from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import require_admin
from app.schemas.deposit import DepositLedgerResponse

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
