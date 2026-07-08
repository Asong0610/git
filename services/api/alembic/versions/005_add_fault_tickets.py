"""创建 fault_repair_tickets 表。"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision = "005_add_fault_tickets"
down_revision = "004_add_student_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fault_repair_tickets",
        sa.Column("id", sa.CHAR(36), nullable=False),
        sa.Column("device_id", sa.CHAR(36), nullable=False),
        sa.Column("user_id", sa.CHAR(36), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("admin_remark", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        op.f("ix_fault_repair_tickets_device_id"),
        "fault_repair_tickets",
        ["device_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_fault_repair_tickets_user_id"),
        "fault_repair_tickets",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_fault_repair_tickets_status"),
        "fault_repair_tickets",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_fault_repair_tickets_status"), table_name="fault_repair_tickets")
    op.drop_index(op.f("ix_fault_repair_tickets_user_id"), table_name="fault_repair_tickets")
    op.drop_index(op.f("ix_fault_repair_tickets_device_id"), table_name="fault_repair_tickets")
    op.drop_table("fault_repair_tickets")