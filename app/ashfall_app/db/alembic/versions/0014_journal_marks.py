"""The marks each composed day's page carries (saves/journal.py, statement 21), as a JSON list of mark kinds (expand
only: the build before this one never writes it, and its rows read as no marks)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("save_journal", sa.Column("marks", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")))


def downgrade() -> None:
    op.drop_column("save_journal", "marks")
