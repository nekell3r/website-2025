"""correct types

Revision ID: 15770dc3d245
Revises: 8921200f04ab
Create Date: 2025-03-24 22:52:51.870404

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "15770dc3d245"
down_revision: Union[str, None] = "8921200f04ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
