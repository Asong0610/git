"""故障报修路由：用户提交与查询报修工单。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.schemas.fault import (
    FaultCreateRequest,
    FaultItemResponse,
    FaultListResponse,
)
from app.services.faults import create_fault_ticket, get_user_fault_tickets

router = APIRouter(prefix="/faults", tags=["故障报修"])


@router.post("", response_model=FaultItemResponse)
def submit_fault(
    body: FaultCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户提交设备故障报修。"""
    ticket = create_fault_ticket(
        db,
        user,
        device_id=body.device_id,
        description=body.description,
    )
    return FaultItemResponse.model_validate(ticket)


@router.get("/mine", response_model=FaultListResponse)
def list_my_faults(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户查看自己的报修记录。"""
    items, total = get_user_fault_tickets(db, user, page=page, page_size=page_size)
    return FaultListResponse(
        items=[FaultItemResponse.model_validate(item) for item in items],
        total=total,
    )