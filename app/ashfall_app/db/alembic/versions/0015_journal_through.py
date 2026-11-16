"""The save time each journal day was composed through (saves/journal_write.py): a day whose `through` is before its end
is still being written (expand only: the build before this one never reads it, and a row it stored, `through` null, is
a day composed whole)."""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("save_journal", sa.Column("through", sa.BigInteger, nullable=True))


def downgrade() -> None:
    op.drop_column("save_journal", "through")
