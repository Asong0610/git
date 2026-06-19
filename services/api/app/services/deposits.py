"""押金服务。"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.deposit_ledger import DepositLedger


def freeze_deposit(
    db: Session,
    user: User,
    amount: Decimal,
    order_id: str | None = None,
) -> DepositLedger:
    """冻结（扣减）押金。"""
    amount = amount.quantize(Decimal("0.01"))
    user.deposit_balance -= amount

    ledger = DepositLedger(
        user_id=user.id,
        order_id=order_id,
        entry_type="freeze",
        amount=-amount,
        balance_after=user.deposit_balance,
        remark="借出冻结",
    )
    db.add(ledger)
    return ledger


def refund_deposit(
    db: Session,
    user_id: str,
    amount: Decimal,
    order_id: str | None = None,
    remark: str = "押金退还",
) -> DepositLedger:
    """退还押金。"""
    amount = amount.quantize(Decimal("0.01"))
    user = db.get(User, user_id)
    user.deposit_balance += amount

    ledger = DepositLedger(
        user_id=user_id,
        order_id=order_id,
        entry_type="refund",
        amount=amount,
        balance_after=user.deposit_balance,
        remark=remark,
    )
    db.add(ledger)
    return ledger


def topup_deposit(
    db: Session,
    user: User,
    amount: Decimal,
) -> DepositLedger:
    """押金充值。"""
    amount = amount.quantize(Decimal("0.01"))
    user.deposit_balance += amount

    ledger = DepositLedger(
        user_id=user.id,
        entry_type="topup",
        amount=amount,
        balance_after=user.deposit_balance,
        remark="押金充值",
    )
    db.add(ledger)
    db.commit()
    db.refresh(ledger)
    return ledger


def record_ledger(
    db: Session,
    user_id: str,
    entry_type: str,
    amount: Decimal,
    balance_after: Decimal,
    order_id: str | None = None,
    remark: str | None = None,
) -> DepositLedger:
    """通用押金流水记录。"""
    ledger = DepositLedger(
        user_id=user_id,
        order_id=order_id,
        entry_type=entry_type,
        amount=amount.quantize(Decimal("0.01")),
        balance_after=balance_after.quantize(Decimal("0.01")),
        remark=remark,
    )
    db.add(ledger)
    return ledger


def get_user_ledger(
    db: Session,
    user: User,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DepositLedger], int]:
    """查询用户押金流水。"""
    from sqlalchemy import select as sa_select

    stmt = sa_select(DepositLedger).where(DepositLedger.user_id == user.id)
    count_stmt = sa_select(DepositLedger).where(DepositLedger.user_id == user.id)
    total = len(db.execute(count_stmt).scalars().all())

    stmt = stmt.order_by(DepositLedger.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars().all())
    return items, total
