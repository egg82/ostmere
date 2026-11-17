"""The player's own earlier best per goal (saves/mixbest.py), kept on the save's row. Expand only: the build before
this one never reads the column."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("mix_best", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("saves", "mix_best")
