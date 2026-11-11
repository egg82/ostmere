"""What the rules did lately (expand only, so the build before this one runs on it unchanged): each save keeps one entry
per rule, written and pruned by saves/ruleruns.py; null on a save no write of this build has touched."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("rule_runs", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("saves", "rule_runs")
