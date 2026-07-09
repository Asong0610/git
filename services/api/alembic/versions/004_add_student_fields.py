"""添加 student_id 与 name 字段到 users 表。"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision = "004_add_student_fields"
down_revision = "003_rename_overdue_fee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("student_id", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("name", sa.String(length=50), nullable=True),
    )
    op.create_index(op.f("ix_users_student_id"), "users", ["student_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_student_id"), table_name="users")
    op.drop_column("users", "name")
    op.drop_column("users", "student_id")