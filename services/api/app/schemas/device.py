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


class DeviceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128, description="设备名称")
    category: str | None = Field(default=None, max_length=64, description="分类")
    location: str | None = Field(default=None, max_length=256, description="位置")
    hourly_rate: Decimal | None = Field(default=None, gt=0, description="每小时费率")
    status: str | None = Field(default=None, description="状态")
