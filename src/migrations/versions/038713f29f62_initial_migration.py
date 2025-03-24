"""initial migration

Revision ID: 038713f29f62
Revises:
Create Date: 2025-03-24 22:39:35.362199

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "038713f29f62"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=25), nullable=False),
        sa.Column("exam", sa.String(length=10), nullable=False),
        sa.Column("result", sa.Integer(), nullable=False),
        sa.Column("review", sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("reviews")
