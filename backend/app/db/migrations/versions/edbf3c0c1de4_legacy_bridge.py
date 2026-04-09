"""legacy bridge revision

Revision ID: edbf3c0c1de4
Revises: d37238fc3c7a
Create Date: 2026-02-14 20:10:00

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "edbf3c0c1de4"
down_revision: Union[str, Sequence[str], None] = "d37238fc3c7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This revision exists only for compatibility with databases
    # that were previously stamped/migrated to edbf3c0c1de4.
    pass


def downgrade() -> None:
    pass
