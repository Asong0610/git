"""押金流水相关 Schema。"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class DepositLedgerResponse(BaseModel):
    id: str = Field(..., description="流水 ID")
    entry_type: str = Field(..., description="类型")
    amount: Decimal = Field(..., description="金额")
    balance_after: Decimal = Field(..., description="变动后余额")
    remark: str | None = Field(default=None, description="备注")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class DepositLedgerListResponse(BaseModel):
    items: list[DepositLedgerResponse] = Field(default_factory=list)
    total: int = Field(..., description="总数")
