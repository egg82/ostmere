"""Devices that asked to be reminded to play (expand only, so the build before this one runs on it unchanged): a row is
a device with reminders on, no row is off."""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reminder_devices",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("account_id", sa.BigInteger, sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.Text, nullable=False, unique=True),
        sa.Column("p256dh", sa.Text, nullable=False),
        sa.Column("auth", sa.Text, nullable=False),
        sa.Column("after_hours", sa.Integer, nullable=False),
        sa.Column("tz", sa.Text, nullable=False),
        sa.Column("send_from_hour", sa.Integer, nullable=False),
        sa.Column("send_until_hour", sa.Integer, nullable=False),
        sa.Column("visited_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.CheckConstraint("send_from_hour BETWEEN 0 AND 23 AND send_until_hour BETWEEN 0 AND 23",
                           name="ck_reminder_devices_send_hours"),
    )
    op.create_index("ix_reminder_devices_account_id", "reminder_devices", ["account_id"])
    op.create_index("ix_reminder_devices_visited_at", "reminder_devices", ["visited_at"])


def downgrade() -> None:
    op.drop_table("reminder_devices")
