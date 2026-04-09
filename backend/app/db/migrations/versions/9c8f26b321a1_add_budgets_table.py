"""add budgets table

Revision ID: 9c8f26b321a1
Revises: edbf3c0c1de4
Create Date: 2026-02-14 19:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c8f26b321a1"
down_revision: Union[str, Sequence[str], None] = "edbf3c0c1de4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("budgets"):
        return

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("limit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("limit_amount > 0", name="check_budget_limit_positive"),
        sa.CheckConstraint("period_start <= period_end", name="check_budget_period_valid"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", "period_start", "period_end", name="uq_budget_user_category_period"),
    )
    op.create_index(op.f("ix_budgets_user_id"), "budgets", ["user_id"], unique=False)
    op.create_index(op.f("ix_budgets_category_id"), "budgets", ["category_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("budgets"):
        return

    op.drop_index(op.f("ix_budgets_category_id"), table_name="budgets")
    op.drop_index(op.f("ix_budgets_user_id"), table_name="budgets")
    op.drop_table("budgets")
