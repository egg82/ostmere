"""Several games on one account (expand only, so the build before this one runs on it unchanged): each save's number
among its account's games, backfilled in id order, and the Camp levels it had landed when last written (null until a
build that keeps it writes the save); an index on deleted_at for the writer that deletes held saves for good."""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("number", sa.Integer, nullable=True))
    op.add_column("saves", sa.Column("camp_level", sa.Integer, nullable=True))
    op.execute("UPDATE saves SET number = r.n FROM (SELECT id, row_number() OVER (PARTITION BY account_id ORDER BY id)"
               " AS n FROM saves) AS r WHERE saves.id = r.id")
    op.create_index("ix_saves_deleted_at", "saves", ["deleted_at"], postgresql_where=sa.text("deleted_at IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("ix_saves_deleted_at", "saves")
    op.drop_column("saves", "camp_level")
    op.drop_column("saves", "number")
