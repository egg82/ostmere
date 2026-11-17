"""The writer queue's counts for today (docs/decisions/writer.md, layer 4): a world's weight and the calls it has
spent, so a restart keeps the day's caps. Expand only: no running build reads the table."""

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "writer_day",
        sa.Column("day", sa.Date, nullable=False),
        sa.Column("save_id", sa.Text, nullable=False),
        sa.Column("weight", sa.Integer, nullable=False),
        sa.Column("spent", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("day", "save_id"),
    )


def downgrade() -> None:
    op.drop_table("writer_day")
