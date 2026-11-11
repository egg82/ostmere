"""Lessons are kept per save, and the account can turn them off (expand only, so the build before this one runs on it
unchanged): what the page keeps about one save's teaching ({} on every save made before this column), and the
account's lessons setting (on until the player turns it off)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("presentation", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column("accounts", sa.Column("lessons", sa.Boolean, nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("accounts", "lessons")
    op.drop_column("saves", "presentation")
