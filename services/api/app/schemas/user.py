"""用户相关 Schema。"""

from decimal import Decimal
from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    id: str = Field(..., description="用户 ID")
    phone: str = Field(..., description="手机号")
    nickname: str | None = Field(default=None, description="昵称")
    deposit_balance: Decimal = Field(..., description="押金余额")
    role: str = Field(..., description="角色")
    status: str = Field(..., description="状态")

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=64, description="昵称")


class DepositTopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="充值金额")
