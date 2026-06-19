"""认证相关 Schema。"""

from pydantic import BaseModel, Field


class SmsCodeRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")


class SmsCodeResponse(BaseModel):
    message: str = Field(default="验证码已发送", description="提示信息")
    debug_code: str | None = Field(default=None, description="开发环境验证码（生产环境为 null）")


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    sms_code: str = Field(..., min_length=4, max_length=8, description="短信验证码")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
