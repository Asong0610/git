"""设备相关 Schema。"""

from decimal import Decimal
from pydantic import BaseModel, Field


class DeviceResponse(BaseModel):
    id: str = Field(..., description="设备 ID")
    device_code: str = Field(..., description="设备业务码")
    name: str = Field(..., description="设备名称")
    category: str | None = Field(default=None, description="分类")
    location: str | None = Field(default=None, description="位置")
    hourly_rate: Decimal = Field(..., description="每小时费率")
    deposit_amount: Decimal = Field(default=Decimal("0.00"), description="固定押金")
    free_hours: int = Field(default=2, description="免费时长（小时）")
    status: str = Field(..., description="状态")

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse] = Field(default_factory=list)
    total: int = Field(..., description="总数")


class DeviceCreateRequest(BaseModel):
    device_code: str = Field(..., min_length=1, max_length=32, description="设备业务码")
    name: str = Field(..., min_length=1, max_length=128, description="设备名称")
    category: str | None = Field(default=None, max_length=64, description="分类")
    location: str | None = Field(default=None, max_length=256, description="位置")
    hourly_rate: Decimal = Field(..., gt=0, description="每小时费率")
    deposit_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="固定押金")
    free_hours: int = Field(default=2, ge=0, description="免费时长（小时）")


class DeviceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128, description="设备名称")
    category: str | None = Field(default=None, max_length=64, description="分类")
    location: str | None = Field(default=None, max_length=256, description="位置")
    hourly_rate: Decimal | None = Field(default=None, gt=0, description="每小时费率")
    deposit_amount: Decimal | None = Field(default=None, ge=0, description="固定押金")
    free_hours: int | None = Field(default=None, ge=0, description="免费时长（小时）")
    status: str | None = Field(default=None, description="状态")
