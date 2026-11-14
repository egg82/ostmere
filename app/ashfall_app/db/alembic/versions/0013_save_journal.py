"""The journal's composed days, one row per save and game day (expand only: the build before this one never reads it).
A save that has no rows composes all of its closed days on its next step (saves/journal_write.py)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "save_journal",
        sa.Column("save_id", sa.BigInteger, sa.ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("day", sa.Integer, primary_key=True),
        sa.Column("notes", JSONB, nullable=False),
        sa.Column("gap", sa.Text, nullable=True),
        sa.CheckConstraint("gap IN ('busy', 'away')", name="ck_save_journal_gap"),
    )


def downgrade() -> None:
    op.drop_table("save_journal")
