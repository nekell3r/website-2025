"""reformate

Revision ID: 518b16625c4c
Revises: 1c2f807c3cb7
Create Date: 2025-04-19 18:01:26.023269

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "518b16625c4c"
down_revision: Union[str, None] = "1c2f807c3cb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("products", sa.Column("price", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("products", "price")
    # ### end Alembic commands ###
