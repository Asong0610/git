"""统计相关 Schema。"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class StatisticsQuery(BaseModel):
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    group_by: Literal["day", "week", "month"] = Field(default="day", description="时间分组维度")


class TimeStatsItem(BaseModel):
    period: str = Field(..., description="统计周期")
    borrow_count: int = Field(..., description="借用次数")
    total_hours: float = Field(..., description="累计使用时长（小时）")
    total_revenue: Decimal = Field(..., description="营收金额（元）")

    model_config = {"from_attributes": True}


class DeviceStatsItem(BaseModel):
    device_code: str = Field(..., description="设备编号")
    device_name: str = Field(..., description="设备名称")
    category: str | None = Field(default=None, description="分类")
    borrow_count: int = Field(..., description="借用次数")
    total_hours: float = Field(..., description="累计使用时长（小时）")
    total_revenue: Decimal = Field(..., description="营收金额（元）")

    model_config = {"from_attributes": True}