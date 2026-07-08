"""订单统计服务。"""

from datetime import date, datetime, timedelta
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.models.borrow_order import BorrowOrder
from app.db.models.device import Device


_DATE_FORMATS = {
    "day": "%Y-%m-%d",
    "week": "%x-W%v",
    "month": "%Y-%m",
}


def get_time_statistics(
    db: Session,
    start_date: date,
    end_date: date,
    group_by: str,
) -> list[dict]:
    """按时间维度聚合已归还订单的统计数据。"""
    date_format = _DATE_FORMATS.get(group_by, _DATE_FORMATS["day"])
    # 包含 end_date 当天
    end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

    stmt = (
        select(
            func.date_format(BorrowOrder.returned_at, date_format).label("period"),
            func.count().label("borrow_count"),
            (func.sum(func.timestampdiff(text("MINUTE"), BorrowOrder.borrowed_at, BorrowOrder.returned_at)) / 60.0).label("total_hours"),
            func.sum(BorrowOrder.usage_fee).label("total_revenue"),
        )
        .where(BorrowOrder.status == "returned")
        .where(BorrowOrder.returned_at >= start_date)
        .where(BorrowOrder.returned_at < end_datetime)
        .group_by("period")
        .order_by("period")
    )

    rows = db.execute(stmt).all()
    return [
        {
            "period": row.period,
            "borrow_count": row.borrow_count,
            "total_hours": float(row.total_hours or 0),
            "total_revenue": row.total_revenue or 0,
        }
        for row in rows
    ]


def get_device_statistics(
    db: Session,
    start_date: date,
    end_date: date,
) -> list[dict]:
    """按设备维度聚合已归还订单的统计数据。"""
    end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

    stmt = (
        select(
            Device.device_code.label("device_code"),
            Device.name.label("device_name"),
            Device.category.label("category"),
            func.count().label("borrow_count"),
            (func.sum(func.timestampdiff(text("MINUTE"), BorrowOrder.borrowed_at, BorrowOrder.returned_at)) / 60.0).label("total_hours"),
            func.sum(BorrowOrder.usage_fee).label("total_revenue"),
        )
        .join(Device, BorrowOrder.device_id == Device.id)
        .where(BorrowOrder.status == "returned")
        .where(BorrowOrder.returned_at >= start_date)
        .where(BorrowOrder.returned_at < end_datetime)
        .group_by(Device.id)
        .order_by(func.count().desc())
    )

    rows = db.execute(stmt).all()
    return [
        {
            "device_code": row.device_code,
            "device_name": row.device_name,
            "category": row.category,
            "borrow_count": row.borrow_count,
            "total_hours": float(row.total_hours or 0),
            "total_revenue": row.total_revenue or 0,
        }
        for row in rows
    ]


def export_statistics_excel(
    db: Session,
    start_date: date,
    end_date: date,
    group_by: str,
) -> BytesIO:
    """生成统计数据的 Excel 文件并返回 BytesIO 对象。"""
    time_stats = get_time_statistics(db, start_date, end_date, group_by)
    device_stats = get_device_statistics(db, start_date, end_date)

    wb = Workbook()

    # Sheet1: 按时间汇总
    ws_time = wb.active
    ws_time.title = "按时间汇总"
    ws_time.append(["统计周期", "借用次数", "使用时长(小时)", "营收(元)"])
    total_count = 0
    total_hours = 0.0
    total_revenue = 0
    for item in time_stats:
        ws_time.append([
            item["period"],
            item["borrow_count"],
            round(item["total_hours"], 2),
            float(item["total_revenue"]),
        ])
        total_count += item["borrow_count"]
        total_hours += item["total_hours"]
        total_revenue += float(item["total_revenue"])
    ws_time.append(["汇总", total_count, round(total_hours, 2), total_revenue])

    # Sheet2: 按设备汇总
    ws_device = wb.create_sheet(title="按设备汇总")
    ws_device.append(["设备编号", "设备名称", "分类", "借用次数", "使用时长(小时)", "营收(元)"])
    for item in device_stats:
        ws_device.append([
            item["device_code"],
            item["device_name"],
            item["category"] or "",
            item["borrow_count"],
            round(item["total_hours"], 2),
            float(item["total_revenue"]),
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer