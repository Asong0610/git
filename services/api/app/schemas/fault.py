"""故障报修工单相关 Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FaultCreateRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=36, description="设备 ID")
    description: str = Field(
        ..., min_length=1, max_length=500, description="故障描述"
    )


class FaultProcessRequest(BaseModel):
    status: Literal["processing", "resolved", "closed"] = Field(..., description="处理状态")
    admin_remark: str | None = Field(default=None, max_length=500, description="管理员备注")


class FaultItemResponse(BaseModel):
    id: str = Field(..., description="工单 ID")
    device_id: str = Field(..., description="设备 ID")
    user_id: str = Field(..., description="报修用户 ID")
    description: str = Field(..., description="故障描述")
    status: str = Field(..., description="工单状态")
    admin_remark: str | None = Field(default=None, description="管理员备注")
    resolved_at: datetime | None = Field(default=None, description="解决时间")
    created_at: datetime = Field(..., description="报修时间")
    updated_at: datetime = Field(..., description="更新时间")
    device_name: str | None = Field(default=None, description="设备名称")
    user_phone: str | None = Field(default=None, description="报修用户手机号")

    model_config = {"from_attributes": True}


class FaultListResponse(BaseModel):
    items: list[FaultItemResponse] = Field(default_factory=list)
    total: int = Field(..., description="总数")