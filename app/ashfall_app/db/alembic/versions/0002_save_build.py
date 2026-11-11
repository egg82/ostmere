"""Which build last wrote each save and under which content release, so a pod never writes over a save of a later
release (expand only: both nullable, and the build before this one writes no saves); and an index for pruning
accounts by last use."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("build", sa.Text, nullable=True))
    op.add_column("saves", sa.Column("release", sa.Integer, nullable=True))
    op.create_index("ix_accounts_last_seen_at", "accounts", ["last_seen_at"])


def downgrade() -> None:
    op.drop_index("ix_accounts_last_seen_at", "accounts")
    op.drop_column("saves", "release")
    op.drop_column("saves", "build")
