"""将 free_hours 改为 free_minutes，默认 5 分钟。"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "003_free_hours_to_minutes"
down_revision: Union[str, None] = "002_add_deposit_free_hours"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column("free_minutes", sa.Integer(), server_default="5", nullable=False),
    )
    # 将已有的 free_hours 值转为分钟
    op.execute("UPDATE devices SET free_minutes = free_hours * 60")
    op.drop_column("devices", "free_hours")


def downgrade() -> None:
    op.add_column(
        "devices",
        sa.Column("free_hours", sa.Integer(), server_default="2", nullable=False),
    )
    op.execute("UPDATE devices SET free_hours = free_minutes / 60")
    op.drop_column("devices", "free_minutes")
