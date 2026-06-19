"""用户路由：个人信息、押金充值。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.dependencies import get_db
from app.dependencies import get_current_user
from app.schemas.deposit import DepositLedgerListResponse, DepositLedgerResponse
from app.schemas.user import UserProfileResponse, UserUpdateRequest, DepositTopUpRequest
from app.services.deposits import topup_deposit, get_user_ledger

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    """获取当前用户信息。"""
    return UserProfileResponse(
        id=str(user.id),
        phone=user.phone,
        nickname=user.nickname,
        deposit_balance=user.deposit_balance,
        role=user.role,
        status=user.status,
    )


@router.patch("/me", response_model=UserProfileResponse)
def update_profile(
    body: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人信息。"""
    if body.nickname is not None:
        user.nickname = body.nickname
    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        id=str(user.id),
        phone=user.phone,
        nickname=user.nickname,
        deposit_balance=user.deposit_balance,
        role=user.role,
        status=user.status,
    )


@router.post("/me/deposit/topup", response_model=UserProfileResponse)
def deposit_topup(
    body: DepositTopUpRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """押金充值。"""
    topup_deposit(db, user, body.amount)
    db.refresh(user)

    return UserProfileResponse(
        id=str(user.id),
        phone=user.phone,
        nickname=user.nickname,
        deposit_balance=user.deposit_balance,
        role=user.role,
        status=user.status,
    )


@router.get("/me/deposit/ledger", response_model=DepositLedgerListResponse)
def get_deposit_ledger(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询押金流水。"""
    items, total = get_user_ledger(db, user, page=page, page_size=page_size)
    return DepositLedgerListResponse(
        items=[
            DepositLedgerResponse(
                id=str(item.id),
                entry_type=item.entry_type,
                amount=item.amount,
                balance_after=item.balance_after,
                remark=item.remark,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
    )
