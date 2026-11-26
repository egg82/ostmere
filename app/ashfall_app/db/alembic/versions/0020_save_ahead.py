"""A save's catch-up computed ahead while its player is away (saves/ahead.py). Expand only: no running build reads the
table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "save_ahead",
        sa.Column("save_id", sa.BigInteger, sa.ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("base", sa.Text, nullable=False),
        sa.Column("rules_digest", sa.Text, nullable=False),
        sa.Column("release", sa.Integer, nullable=False),
        sa.Column("game_time", sa.BigInteger, nullable=False),
        sa.Column("state", sa.Text, nullable=False),
        sa.Column("lines", JSONB, nullable=False),
        sa.Column("rule_runs", JSONB, nullable=True),
        sa.Column("written_at", TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("save_ahead")
