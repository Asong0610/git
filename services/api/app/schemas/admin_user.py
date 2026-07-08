"""管理端用户相关 Schema。"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class UserItemResponse(BaseModel):
    id: str = Field(..., description="用户 ID")
    student_id: str | None = Field(default=None, description="学号")
    name: str | None = Field(default=None, description="真实姓名")
    phone: str = Field(..., description="手机号")
    deposit_balance: Decimal = Field(..., description="押金余额")
    status: str = Field(..., description="账号状态")
    created_at: datetime = Field(..., description="注册时间")

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserItemResponse] = Field(default_factory=list, description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")


class FreezeRequest(BaseModel):
    action: Literal["freeze", "unfreeze"] = Field(..., description="冻结/解冻")