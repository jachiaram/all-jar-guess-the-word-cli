"""Add seen_words to players

Revision ID: 2f94a8d1c7b3
Revises: 7f0e8d2b4c19
Create Date: 2026-06-26 12:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2f94a8d1c7b3"
down_revision: Union[str, Sequence[str], None] = "7f0e8d2b4c19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "players",
        sa.Column(
            "seen_words",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("players", "seen_words")
