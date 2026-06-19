"""认证路由：短信验证码、登录、刷新令牌。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.db.models.user import User
from app.schemas.auth import (
    SmsCodeRequest,
    SmsCodeResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/sms-code", response_model=SmsCodeResponse)
def send_sms_code(body: SmsCodeRequest, db: Session = Depends(get_db)):
    """发送短信验证码（开发环境返回固定码）。"""
    # 自动注册用户（首次登录）
    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        role = "admin" if body.phone == "13800138000" else "user"
        user = User(phone=body.phone, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif body.phone == "13800138000" and user.role != "admin":
        # 如果测试手机号已存在但不是 admin，强制提权
        user.role = "admin"
        db.commit()
        db.refresh(user)

    debug_code = auth_service.generate_sms_code(body.phone)
    return SmsCodeResponse(debug_code=debug_code)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """手机号 + 验证码登录。"""
    if not auth_service.verify_sms_code(body.phone, body.sms_code):
        from app.core.exceptions import AppError
        raise AppError("验证码错误或已过期", code="INVALID_SMS_CODE", status_code=401)

    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        from app.core.exceptions import AppError
        raise AppError("用户不存在", code="USER_NOT_FOUND", status_code=404)
    if user.status != "active":
        from app.core.exceptions import AppError
        raise AppError("账号已被禁用", code="ACCOUNT_DISABLED", status_code=403)

    access_token, access_expires = auth_service.create_access_token(
        str(user.id), user.phone, user.role
    )
    refresh_token, refresh_expires = auth_service.create_refresh_token(
        str(user.id), user.phone, user.role
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_expires,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenRequest):
    """使用 refresh token 换取新令牌。"""
    payload = auth_service.decode_token(body.refresh_token, token_type="refresh")
    if not payload:
        from app.core.exceptions import AppError
        raise AppError("刷新令牌无效或已过期", code="INVALID_REFRESH_TOKEN", status_code=401)

    access_token, access_expires = auth_service.create_access_token(
        payload["sub"], payload["phone"], payload["role"]
    )
    refresh_token, refresh_expires = auth_service.create_refresh_token(
        payload["sub"], payload["phone"], payload["role"]
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_expires,
    )
