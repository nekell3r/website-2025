"""add foreign key

Revision ID: 8921200f04ab
Revises: 038713f29f62
Create Date: 2025-03-24 22:43:15.415920

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8921200f04ab"
down_revision: Union[str, None] = "038713f29f62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=25), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("telephone", sa.String(length=15), nullable=False),
        sa.Column("password", sa.String(length=50), nullable=False),
        sa.Column("exam", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("reviews", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_foreign_key(None, "reviews", "users", ["user_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "reviews", type_="foreignkey")
    op.drop_column("reviews", "user_id")
    op.drop_table("users")
