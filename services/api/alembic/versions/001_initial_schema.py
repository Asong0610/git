"""初始迁移：users、devices、borrow_orders、deposit_ledger 四张核心表（MySQL 兼容）。"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
    "users",
    sa.Column("id", sa.CHAR(36), nullable=False),
    sa.Column("phone", sa.String(length=20), nullable=False),
    sa.Column("nickname", sa.String(length=64), nullable=True),
    sa.Column("deposit_balance", sa.Numeric(precision=12, scale=2), server_default="0.00", nullable=False),
    sa.Column("role", sa.String(length=16), server_default="user", nullable=False),
    sa.Column("status", sa.String(length=16), server_default="active", nullable=False),
    sa.Column("created_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    sa.Column("updated_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("phone"),
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
  )
  op.create_index("ix_users_phone", "users", ["phone"], unique=False)
  op.create_index("ix_users_status", "users", ["status"], unique=False)

  op.create_table(
    "devices",
    sa.Column("id", sa.CHAR(36), nullable=False),
    sa.Column("device_code", sa.String(length=32), nullable=False),
    sa.Column("name", sa.String(length=128), nullable=False),
    sa.Column("category", sa.String(length=64), nullable=True),
    sa.Column("location", sa.String(length=256), nullable=True),
    sa.Column("hourly_rate", sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column("status", sa.String(length=16), server_default="available", nullable=False),
    sa.Column("created_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    sa.Column("updated_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("device_code"),
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
  )
  op.create_index("ix_devices_device_code", "devices", ["device_code"], unique=False)
  op.create_index("ix_devices_category", "devices", ["category"], unique=False)
  op.create_index("ix_devices_status", "devices", ["status"], unique=False)

  op.create_table(
    "borrow_orders",
    sa.Column("id", sa.CHAR(36), nullable=False),
    sa.Column("user_id", sa.CHAR(36), nullable=False),
    sa.Column("device_id", sa.CHAR(36), nullable=False),
    sa.Column("status", sa.String(length=16), nullable=False),
    sa.Column("borrowed_at", sa.DATETIME(), nullable=False),
    sa.Column("due_at", sa.DATETIME(), nullable=False),
    sa.Column("returned_at", sa.DATETIME(), nullable=True),
    sa.Column("overdue_fee", sa.Numeric(precision=12, scale=2), server_default="0.00", nullable=False),
    sa.Column("idempotency_key", sa.String(length=64), nullable=False),
    sa.Column("return_idempotency_key", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    sa.Column("updated_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
    sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("idempotency_key"),
    sa.UniqueConstraint("return_idempotency_key"),
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
  )
  op.create_index("ix_borrow_orders_device_id", "borrow_orders", ["device_id"], unique=False)
  op.create_index("ix_borrow_orders_due_at", "borrow_orders", ["due_at"], unique=False)
  op.create_index("ix_borrow_orders_status", "borrow_orders", ["status"], unique=False)
  op.create_index("ix_borrow_orders_user_id", "borrow_orders", ["user_id"], unique=False)

  op.create_table(
    "deposit_ledger",
    sa.Column("id", sa.CHAR(36), nullable=False),
    sa.Column("user_id", sa.CHAR(36), nullable=False),
    sa.Column("order_id", sa.CHAR(36), nullable=True),
    sa.Column("entry_type", sa.String(length=32), nullable=False),
    sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column("balance_after", sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column("remark", sa.String(length=256), nullable=True),
    sa.Column("created_at", sa.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    sa.ForeignKeyConstraint(["order_id"], ["borrow_orders.id"]),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    sa.PrimaryKeyConstraint("id"),
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
  )
  op.create_index("ix_deposit_ledger_created_at", "deposit_ledger", ["created_at"], unique=False)
  op.create_index("ix_deposit_ledger_user_id", "deposit_ledger", ["user_id"], unique=False)


def downgrade() -> None:
  op.drop_index("ix_deposit_ledger_user_id", table_name="deposit_ledger")
  op.drop_index("ix_deposit_ledger_created_at", table_name="deposit_ledger")
  op.drop_table("deposit_ledger")

  op.drop_index("ix_borrow_orders_user_id", table_name="borrow_orders")
  op.drop_index("ix_borrow_orders_status", table_name="borrow_orders")
  op.drop_index("ix_borrow_orders_due_at", table_name="borrow_orders")
  op.drop_index("ix_borrow_orders_device_id", table_name="borrow_orders")
  op.drop_table("borrow_orders")

  op.drop_index("ix_devices_status", table_name="devices")
  op.drop_index("ix_devices_category", table_name="devices")
  op.drop_index("ix_devices_device_code", table_name="devices")
  op.drop_table("devices")

  op.drop_index("ix_users_status", table_name="users")
  op.drop_index("ix_users_phone", table_name="users")
  op.drop_table("users")
