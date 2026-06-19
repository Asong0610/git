"""Stage 1 集成测试：验证 API 路由注册 + 基础设施连通性。"""

import sys
import os
import json

# 确保项目路径可用
sys.path.insert(0, os.path.dirname(__file__))


def test_routes_registered():
    """验证所有路由已正确注册到 FastAPI 应用。"""
    from app.main import app

    from collections import defaultdict
    route_map = defaultdict(set)
    for r in app.routes:
        if hasattr(r, "methods") and r.path.startswith("/api/v1"):
            route_map[r.path].update(r.methods)
    routes = dict(route_map)

    print("\n=== 已注册的路由 ===")
    for path, methods in sorted(routes.items()):
        print(f"  {sorted(methods)}  {path}")

    # 将所有路由方法合并为 {path: set_of_methods}
    merged = {}
    for path, methods in routes.items():
        merged.setdefault(path, set()).update(methods)

    expected = {
        "/api/v1/health": {"GET"},
        "/api/v1/auth/sms-code": {"POST"},
        "/api/v1/auth/login": {"POST"},
        "/api/v1/auth/refresh": {"POST"},
        "/api/v1/users/me": {"GET", "PATCH"},
        "/api/v1/users/me/deposit/topup": {"POST"},
        "/api/v1/users/me/deposit/ledger": {"GET"},
        "/api/v1/devices": {"GET", "POST"},
        "/api/v1/devices/{device_code}": {"GET", "PUT", "DELETE"},
        "/api/v1/borrows": {"GET", "POST"},
        "/api/v1/borrows/current": {"GET"},
        "/api/v1/borrows/{order_id}": {"GET"},
        "/api/v1/borrows/{order_id}/return": {"POST"},
        "/api/v1/admin/users/{user_id}/deposit/adjust": {"POST"},
    }

    print("\n=== 路由验证 ===")
    all_ok = True
    for path, methods in expected.items():
        if path in merged:
            registered = merged[path]
            if methods.issubset(registered):
                print(f"  OK  {path}")
            else:
                print(f"  MISSING methods on {path}: expected {methods}, got {registered}")
                all_ok = False
        else:
            print(f"  MISSING  {path}")
            all_ok = False

    assert all_ok, "部分路由未注册！"
    print("\n所有路由验证通过！")


def test_health_without_db():
    """验证 health 端点在不连通 DB 时的降级行为。"""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.get("/api/v1/health")
    data = resp.json()
    print(f"\nHealth response: {json.dumps(data, indent=2)}")
    # 无 DB 时应该是 degraded
    assert resp.status_code == 200
    assert data["status"] in ("ok", "degraded")
    print("Health 端点正常响应！")


def test_jwt_token_flow():
    """验证纯 Python JWT 编解码。"""
    from app.services.auth import create_access_token, create_refresh_token, decode_token

    user_id = "test-user-uuid"
    phone = "13800138000"
    role = "user"

    access_token, access_exp = create_access_token(user_id, phone, role)
    refresh_token, refresh_exp = create_refresh_token(user_id, phone, role)

    print(f"\nAccess token (first 30 chars): {access_token[:30]}...")
    print(f"Refresh token (first 30 chars): {refresh_token[:30]}...")

    access_payload = decode_token(access_token, token_type="access")
    assert access_payload is not None
    assert access_payload["sub"] == user_id
    assert access_payload["phone"] == phone
    assert access_payload["role"] == role
    assert access_payload["type"] == "access"
    print("Access token 解码 OK")

    refresh_payload = decode_token(refresh_token, token_type="refresh")
    assert refresh_payload is not None
    assert refresh_payload["type"] == "refresh"
    print("Refresh token 解码 OK")

    # 错误类型应返回 None
    assert decode_token(access_token, token_type="refresh") is None
    print("类型隔离 OK")

    print("\nJWT 令牌全流程验证通过！")


def test_schemas():
    """验证 Pydantic schema 可正常导入与序列化。"""
    from app.schemas.auth import TokenResponse, LoginRequest, SmsCodeRequest
    from app.schemas.user import UserProfileResponse, UserUpdateRequest, DepositTopUpRequest
    from app.schemas.device import DeviceResponse, DeviceCreateRequest, DeviceListResponse
    from app.schemas.borrow import BorrowCreateRequest, BorrowResponse, ReturnResponse
    from app.schemas.deposit import DepositLedgerResponse

    # 测试构造
    token = TokenResponse(access_token="tok", refresh_token="ref", expires_in=3600)
    assert token.token_type == "Bearer"

    login = LoginRequest(phone="13800138000", sms_code="123456")
    assert login.phone == "13800138000"

    device = DeviceCreateRequest(device_code="DEV001", name="充电宝", hourly_rate=2.5)
    assert device.hourly_rate == 2.5

    print("\nSchema 构造验证通过！")


def test_json_encoder():
    """验证 Decimal 全局序列化为字符串。"""
    import json
    from decimal import Decimal
    from app.core.json_encoder import AppJSONEncoder

    data = {"amount": Decimal("10.50"), "rate": Decimal("2.00")}
    result = json.dumps(data, cls=AppJSONEncoder)
    parsed = json.loads(result)
    assert parsed["amount"] == "10.50", f"Expected string, got {parsed['amount']}"
    assert parsed["rate"] == "2.00", f"Expected string, got {parsed['rate']}"
    print("\nDecimal 序列化验证通过！输出为字符串。")


def test_usage_fee_formula():
    """验证计时计费公式：向上取整。"""
    import math
    from decimal import Decimal

    # 模拟：超出免费时长 1.5 小时 -> 应计 2 小时
    hourly_rate = Decimal("10.00")
    extra_seconds = 5400  # 1.5 小时
    extra_hours = math.ceil(extra_seconds / 3600)
    usage_fee = hourly_rate * Decimal(str(extra_hours))
    assert extra_hours == 2
    assert usage_fee == Decimal("20.00")
    print("\n计时计费公式验证通过！（1.5h -> 2h）")


if __name__ == "__main__":
    print("=" * 50)
    print("Stage 1 集成测试")
    print("=" * 50)

    test_routes_registered()
    test_jwt_token_flow()
    test_schemas()
    test_json_encoder()
    test_usage_fee_formula()

    print("\n" + "=" * 50)
    print("所有离线测试通过！")
    print("注意：Health 端点测试需要 Docker 运行 DB + Redis")
    print("请确保 Docker Desktop 已启动后运行完整测试")
    print("=" * 50)
