"""Repeat offers (expand only, so the build before this one runs on it unchanged): each logged decision keeps what held
as it was made (engine DecisionContext as JSON; null on rows written before), and an index that reads a save's recent
decisions of one kind by game time."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("save_decisions", sa.Column("context", JSONB, nullable=True))
    op.create_index("ix_save_decisions_save_id_kind_at", "save_decisions", ["save_id", "kind", "at"])


def downgrade() -> None:
    op.drop_index("ix_save_decisions_save_id_kind_at", "save_decisions")
    op.drop_column("save_decisions", "context")
