"""设备路由：查询、管理。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models.device import Device
from app.dependencies import get_db
from app.dependencies import get_current_user, require_admin
from app.schemas.device import (
    DeviceResponse,
    DeviceListResponse,
    DeviceCreateRequest,
    DeviceUpdateRequest,
)
from app.services.devices import (
    get_device_by_code,
    list_devices,
    create_device,
    update_device,
    delete_device,
)

router = APIRouter(prefix="/devices", tags=["设备"])


@router.get("", response_model=DeviceListResponse)
def list_device_endpoint(
    category: str | None = None,
    status: str | None = None,
    location: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """查询设备列表（支持筛选与分页）。"""
    items, total = list_devices(
        db,
        category=category,
        status=status,
        location=location,
        page=page,
        page_size=page_size,
    )
    return DeviceListResponse(
        items=[
            DeviceResponse(
                id=str(d.id),
                device_code=d.device_code,
                name=d.name,
                category=d.category,
                location=d.location,
                hourly_rate=d.hourly_rate,
                status=d.status,
            )
            for d in items
        ],
        total=total,
    )


@router.get("/{device_code}", response_model=DeviceResponse)
def get_device_endpoint(
    device_code: str,
    db: Session = Depends(get_db),
):
    """按设备码查询设备详情。"""
    device = get_device_by_code(db, device_code)
    if not device:
        from app.core.exceptions import AppError
        raise AppError("设备不存在", code="DEVICE_NOT_FOUND", status_code=404)

    return DeviceResponse(
        id=str(device.id),
        device_code=device.device_code,
        name=device.name,
        category=device.category,
        location=device.location,
        hourly_rate=device.hourly_rate,
        status=device.status,
    )


@router.post("", response_model=DeviceResponse)
def create_device_endpoint(
    body: DeviceCreateRequest,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建设备（管理员）。"""
    existing = get_device_by_code(db, body.device_code)
    if existing:
        from app.core.exceptions import AppError
        raise AppError("设备码已存在", code="DEVICE_CODE_EXISTS", status_code=409)

    device = create_device(
        db,
        device_code=body.device_code,
        name=body.name,
        hourly_rate=body.hourly_rate,
        category=body.category,
        location=body.location,
    )
    return DeviceResponse(
        id=str(device.id),
        device_code=device.device_code,
        name=device.name,
        category=device.category,
        location=device.location,
        hourly_rate=device.hourly_rate,
        status=device.status,
    )


@router.put("/{device_code}", response_model=DeviceResponse)
def update_device_endpoint(
    device_code: str,
    body: DeviceUpdateRequest,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新设备信息（管理员）。"""
    device = get_device_by_code(db, device_code)
    if not device:
        from app.core.exceptions import AppError
        raise AppError("设备不存在", code="DEVICE_NOT_FOUND", status_code=404)

    updates = body.model_dump(exclude_unset=True)
    device = update_device(db, device, updates)

    return DeviceResponse(
        id=str(device.id),
        device_code=device.device_code,
        name=device.name,
        category=device.category,
        location=device.location,
        hourly_rate=device.hourly_rate,
        status=device.status,
    )


@router.delete("/{device_code}", status_code=204)
def delete_device_endpoint(
    device_code: str,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除设备（管理员）。"""
    device = get_device_by_code(db, device_code)
    if not device:
        from app.core.exceptions import AppError
        raise AppError("设备不存在", code="DEVICE_NOT_FOUND", status_code=404)

    delete_device(db, device)
