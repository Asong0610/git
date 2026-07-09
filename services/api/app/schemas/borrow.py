"""借还订单相关 Schema。"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class BorrowCreateRequest(BaseModel):
    device_code: str = Field(..., min_length=1, max_length=32, description="设备业务码")
    idempotency_key: str = Field(..., min_length=1, max_length=64, description="幂等键")


class BorrowResponse(BaseModel):
    id: str = Field(..., description="订单 ID")
    device_code: str = Field(..., description="设备业务码")
    device_name: str = Field(..., description="设备名称")
    borrowed_at: datetime = Field(..., description="借出时间")
    due_at: datetime = Field(..., description="免费截止时间")
    deposit_frozen: Decimal = Field(..., description="冻结押金")

    model_config = {"from_attributes": True}


class ReturnRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=1, max_length=64, description="归还幂等键")


class ReturnResponse(BaseModel):
    id: str = Field(..., description="订单 ID")
    returned_at: datetime = Field(..., description="归还时间")
    actual_hours: float = Field(..., description="实际使用时长（小时）")
    usage_fee: Decimal = Field(..., description="使用费")
    total_fee: Decimal = Field(..., description="总费用")
    deposit_refund: Decimal = Field(..., description="退还押金")

    model_config = {"from_attributes": True}


class OrderItemResponse(BaseModel):
    id: str = Field(..., description="订单 ID")
    device_id: str = Field(..., description="设备 ID")
    device_code: str = Field(..., description="设备业务码")
    device_name: str = Field(..., description="设备名称")
    status: str = Field(..., description="状态")
    borrowed_at: datetime = Field(..., description="借出时间")
    due_at: datetime = Field(..., description="免费截止时间")
    returned_at: datetime | None = Field(default=None, description="归还时间")
    usage_fee: Decimal = Field(..., description="使用费")
    deposit_amount: Decimal = Field(default=Decimal("0.00"), description="冻结押金")

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderItemResponse] = Field(default_factory=list)
    total: int = Field(..., description="总数")


class OrderDetailResponse(BaseModel):
    id: str = Field(..., description="订单 ID")
    device_code: str = Field(..., description="设备业务码")
    device_name: str = Field(..., description="设备名称")
    user_id: str = Field(..., description="用户 ID")
    status: str = Field(..., description="状态")
    borrowed_at: datetime = Field(..., description="借出时间")
    due_at: datetime = Field(..., description="免费截止时间")
    returned_at: datetime | None = Field(default=None, description="归还时间")
    usage_fee: Decimal = Field(..., description="使用费")

    model_config = {"from_attributes": True}
