"""Accounts, their sessions, saves with their decision log, lines and day snapshots, and rate-limit tries."""

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

EMPTY = sa.text("'{}'::jsonb")


def when(name: str, nullable: bool = False) -> sa.Column[datetime]:
    return sa.Column(name, TIMESTAMP(timezone=True), nullable=nullable)


def ident() -> sa.Column[int]:
    return sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True)


def child(name: str) -> sa.Column[int]:
    """The owning save's id, the first half of the row's key."""
    return sa.Column(name, sa.BigInteger, sa.ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True)


def upgrade() -> None:
    op.create_table(
        "accounts", ident(), when("created_at"), when("last_seen_at"),
        sa.Column("presentation", JSONB, nullable=False, server_default=EMPTY))
    op.create_table(
        "sessions", ident(),
        sa.Column("account_id", sa.BigInteger, sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.LargeBinary, nullable=False, unique=True),
        when("created_at"), when("last_seen_at"))
    op.create_index("ix_sessions_account_id", "sessions", ["account_id"])
    op.create_table(
        "saves", ident(),
        sa.Column("account_id", sa.BigInteger, sa.ForeignKey("accounts.id"), nullable=False),
        when("created_at"), when("started_at"), when("updated_at"),
        sa.Column("state", sa.Text, nullable=False),
        sa.Column("format", sa.Integer, nullable=False),
        sa.Column("rules_digest", sa.Text, nullable=False),
        sa.Column("decisions", sa.Integer, nullable=False),
        sa.Column("game_time", sa.BigInteger, nullable=False),
        sa.Column("ended_at", sa.BigInteger, nullable=True),
        sa.Column("presentation", JSONB, nullable=False, server_default=EMPTY),
        when("deleted_at", nullable=True))
    op.create_index("ix_saves_account_id", "saves", ["account_id"])
    op.create_table(
        "save_lines", child("save_id"),
        sa.Column("n", sa.Integer, primary_key=True),
        sa.Column("at", sa.BigInteger, nullable=False),
        sa.Column("key", sa.Text, nullable=False))
    op.create_table(
        "save_decisions", child("save_id"),
        sa.Column("n", sa.Integer, primary_key=True),
        sa.Column("at", sa.BigInteger, nullable=False),
        when("wall"),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("verb", JSONB, nullable=False),
        sa.Column("rules_digest", sa.Text, nullable=False))
    op.create_table(
        "save_snapshots", child("save_id"),
        sa.Column("day", sa.Integer, primary_key=True),
        sa.Column("state", sa.Text, nullable=False),
        sa.Column("rules_digest", sa.Text, nullable=False),
        sa.Column("decisions", sa.Integer, nullable=False))
    op.create_table(
        "tries", ident(),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("who", sa.LargeBinary, nullable=False),
        when("at"))
    op.create_index("ix_tries_kind_who_at", "tries", ["kind", "who", "at"])


def downgrade() -> None:
    for table in ("tries", "save_snapshots", "save_decisions", "save_lines", "saves", "sessions", "accounts"):
        op.drop_table(table)
