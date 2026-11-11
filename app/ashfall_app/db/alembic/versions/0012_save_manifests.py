"""Each rules digest's manifest, stored once (expand only, so the build before this one runs on it unchanged): a save or
snapshot row whose text leaves its manifest out is read with the one held here for its digest."""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "save_manifests",
        sa.Column("rules_digest", sa.Text, primary_key=True),
        sa.Column("manifest", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("save_manifests")
