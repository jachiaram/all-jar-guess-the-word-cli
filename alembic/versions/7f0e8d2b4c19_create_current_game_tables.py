"""Create current game related tables

Revision ID: 7f0e8d2b4c19
Revises: 1c3054c6a12d
Create Date: 2026-06-26 11:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7f0e8d2b4c19"
down_revision: Union[str, Sequence[str], None] = "1c3054c6a12d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


match_value_enum = postgresql.ENUM(
    "full", "partial", "none", name="matchvalue", create_type=False
)
game_status_enum = postgresql.ENUM(
    "in-progress", "won", "lost", name="gamestatus", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    match_value_enum.create(bind, checkfirst=True)
    game_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "current_games",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("secret_word", sa.String(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.UniqueConstraint("player_id"),
    )

    op.create_table(
        "game_guesses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("current_game_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["current_game_id"], ["current_games.id"]),
    )

    op.create_table(
        "guess_letters",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("guess_id", sa.Integer(), nullable=False),
        sa.Column("letter", sa.String(length=1), nullable=False),
        sa.Column("match", match_value_enum, nullable=False),
        sa.ForeignKeyConstraint(["guess_id"], ["game_guesses.id"]),
    )

    op.create_table(
        "game_results",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("current_game_id", sa.Integer(), nullable=False),
        sa.Column("status", game_status_enum, nullable=False),
        sa.Column("word", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["current_game_id"], ["current_games.id"]),
        sa.UniqueConstraint("current_game_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    op.drop_table("game_results")
    op.drop_table("guess_letters")
    op.drop_table("game_guesses")
    op.drop_table("current_games")

    game_status_enum.drop(bind, checkfirst=True)
    match_value_enum.drop(bind, checkfirst=True)
