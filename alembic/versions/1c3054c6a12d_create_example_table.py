"""Create example table

Revision ID: 1c3054c6a12d
Revises: 
Create Date: 2026-06-26 10:06:35.735660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c3054c6a12d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
    """
        CREATE TABLE players (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        );
    """
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
    """
        DROP TABLE players;
    """
    )
