"""The hands-free notice (docs/design/reminders.md, "The hands-free notice"): each save keeps its forecast's hands-free
instant (game seconds and the wall time it maps to), how far that forecast reached, and the instant a notice was sent
for; a device row says whether it takes the notice, and its absence reminder may now be off (after_hours null) while
the notice is on. Expand only: the build before this one never reads the new columns, and every row it writes has
after_hours set."""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("saves", sa.Column("hands_free_at", sa.BigInteger, nullable=True))
    op.add_column("saves", sa.Column("hands_free_wall", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("saves", sa.Column("hands_free_until", sa.BigInteger, nullable=True))
    op.add_column("saves", sa.Column("hands_free_sent", sa.BigInteger, nullable=True))
    op.add_column("reminder_devices", sa.Column("hands_free", sa.Boolean, nullable=False, server_default=sa.false()))
    op.alter_column("reminder_devices", "after_hours", nullable=True)
    op.create_check_constraint("ck_reminder_devices_something_on", "reminder_devices",
                               "after_hours IS NOT NULL OR hands_free")


def downgrade() -> None:
    op.drop_constraint("ck_reminder_devices_something_on", "reminder_devices")
    op.execute("DELETE FROM reminder_devices WHERE after_hours IS NULL")
    op.alter_column("reminder_devices", "after_hours", nullable=False)
    op.drop_column("reminder_devices", "hands_free")
    for c in ("hands_free_sent", "hands_free_until", "hands_free_wall", "hands_free_at"):
        op.drop_column("saves", c)
