"""Contract: a save keeps no presentation (the build before this one neither reads nor writes saves.presentation, so it
runs on the schema without it). The column held only the end card's put-away time, which nothing reads."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("saves", "presentation")


def downgrade() -> None:
    op.add_column("saves", sa.Column("presentation", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")))
