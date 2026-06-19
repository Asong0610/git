"""Decimal 序列化与 Pydantic 类型工具。"""

from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# JSON 响应中将 Decimal 序列化为字符串，避免浮点误差
MoneyDecimal = Annotated[
  Decimal,
  PlainSerializer(lambda value: format(value, "f"), return_type=str),
]
