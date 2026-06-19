"""认证服务：短信验证码、JWT 令牌（标准库实现，无需 PyJWT）。"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone

from app.config import get_settings
from app.core.redis import get_redis_client

SMS_CODE_TTL = 300  # 5 分钟
SMS_DEBUG_CODE = "123456"


# --- JWT helpers (pure Python, HS256) ---

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _sign(header_b64: str, payload_b64: str, secret: str) -> str:
    message = f"{header_b64}.{payload_b64}"
    sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return _b64url(sig)


def _encode_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":"), default=str).encode())
    signature = _sign(header_b64, payload_b64, secret)
    return f"{header_b64}.{payload_b64}.{signature}"


def _decode_jwt(token: str, secret: str) -> dict | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, signature_b64 = parts

    # Verify signature
    expected_sig = _sign(header_b64, payload_b64, secret)
    if not hmac.compare_digest(expected_sig, signature_b64):
        return None

    # Parse payload
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception:
        return None

    # Check expiration
    exp = payload.get("exp")
    if exp and isinstance(exp, (int, float)) and time.time() > exp:
        return None

    return payload


# --- Public API ---

def generate_sms_code(phone: str) -> str:
    """生成并存储短信验证码。开发环境返回固定码。"""
    settings = get_settings()
    redis = get_redis_client()

    code = SMS_DEBUG_CODE if settings.app_env == "development" else secrets.randbelow(900000) + 100000
    code_str = str(code)
    redis.setex(f"sms:{phone}", SMS_CODE_TTL, code_str)
    return code_str


def verify_sms_code(phone: str, code: str) -> bool:
    """校验短信验证码。"""
    redis = get_redis_client()
    stored = redis.get(f"sms:{phone}")
    if stored and stored == code:
        redis.delete(f"sms:{phone}")
        return True
    return False


def create_access_token(user_id: str, phone: str, role: str) -> tuple[str, int]:
    """签发 access token，返回 (token, expires_in_seconds)。"""
    settings = get_settings()
    expires_minutes = settings.jwt_access_expire_minutes
    now_ts = int(time.time())
    payload = {
        "sub": user_id,
        "phone": phone,
        "role": role,
        "exp": now_ts + expires_minutes * 60,
        "iat": now_ts,
        "type": "access",
    }
    token = _encode_jwt(payload, settings.jwt_secret)
    return token, expires_minutes * 60


def create_refresh_token(user_id: str, phone: str, role: str) -> tuple[str, int]:
    """签发 refresh token，返回 (token, expires_in_seconds)。"""
    settings = get_settings()
    expires_days = settings.jwt_refresh_expire_days
    now_ts = int(time.time())
    payload = {
        "sub": user_id,
        "phone": phone,
        "role": role,
        "exp": now_ts + expires_days * 86400,
        "iat": now_ts,
        "type": "refresh",
    }
    token = _encode_jwt(payload, settings.jwt_secret)
    return token, expires_days * 86400


def decode_token(token: str, token_type: str = "access") -> dict | None:
    """解码并校验 token。"""
    settings = get_settings()
    payload = _decode_jwt(token, settings.jwt_secret)
    if payload and payload.get("type") == token_type:
        return payload
    return None
