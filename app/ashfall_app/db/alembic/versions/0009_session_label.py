"""A session's coarse label (expand only, so the build before this one runs on it unchanged): the browser and system it
was made from, for the list of an account's devices; null on a session made before this column."""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("label", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("sessions", "label")
