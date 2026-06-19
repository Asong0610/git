"""FastAPI 依赖注入：数据库会话、JWT 认证。"""

from decimal import Decimal
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

# 直接导入原始 get_db，不再包装，确保全局唯一函数引用
from app.db.session import get_db
from app.db.models.user import User
from app.services import auth as auth_service


def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization header 解析 JWT，获取当前用户。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token = authorization.split(" ", 1)[1]
    payload = auth_service.decode_token(token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user_id = payload["sub"]
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 兜底：防止数据库 default 未生效导致 deposit_balance 为 None
    if user.deposit_balance is None:
        user.deposit_balance = Decimal("0.00")
        db.commit()
        db.refresh(user)

    return user


def require_admin(user: User = Depends(get_current_user)) -> str:
    """校验用户为管理员角色。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return str(user.id)
