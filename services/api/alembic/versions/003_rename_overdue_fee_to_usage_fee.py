"""rename overdue_fee to usage_fee

Revision ID: 003_rename_overdue_fee
Revises: 002_add_deposit_free_hours
Create Date: 2026-06-19

"""
from alembic import op
import sqlalchemy as sa

revision = '003_rename_overdue_fee'
down_revision = '002_add_deposit_free_hours'
branch_labels = None
depends_on = None


def upgrade():
    # 重命名字段
    op.alter_column('borrow_orders', 'overdue_fee', new_column_name='usage_fee')


def downgrade():
    # 回滚
    op.alter_column('borrow_orders', 'usage_fee', new_column_name='overdue_fee')
