"""Tester feedback from the page: the words, the build, and where in the game they were sent (expand only: a new table
no earlier build reads)."""

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def when(name: str) -> sa.Column[datetime]:
    return sa.Column(name, TIMESTAMP(timezone=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "feedback", sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True), when("created_at"),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("build", sa.Text, nullable=False),
        sa.Column("release", sa.Integer, nullable=False),
        sa.Column("account_id", sa.BigInteger, nullable=True),
        sa.Column("save_id", sa.BigInteger, nullable=True),
        sa.Column("game_time", sa.BigInteger, nullable=True),
        sa.Column("last_line", sa.Text, nullable=True))
    op.create_index("ix_feedback_created_at", "feedback", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_feedback_created_at", "feedback")
    op.drop_table("feedback")
