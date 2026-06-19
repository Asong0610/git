"""添加设备押金和免费时长字段。"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_deposit_free_hours"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "deposit_amount",
            sa.Numeric(precision=12, scale=2),
            server_default="0.00",
            nullable=False,
        ),
    )
    op.add_column(
        "devices",
        sa.Column(
            "free_hours",
            sa.Integer(),
            server_default="2",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("devices", "free_hours")
    op.drop_column("devices", "deposit_amount")
