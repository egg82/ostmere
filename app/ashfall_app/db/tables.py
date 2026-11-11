"""The schema as the app's queries see it. Migrations (alembic/versions) build it and never import this file; a test
(tests/db/test_shape.py) holds the two equal.

Ids are identity columns, so an id is never handed out twice, even after its row is deleted. Wall times are timestamptz
written from the app's clock, never a default in SQL; engine times (`at`, `game_time`, `ended_at`) are the engine's own
integer clock. Text sorts by byte: the database is created with C collation and migrate refuses any other."""

from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, ForeignKey, Identity, Index, Integer, LargeBinary, MetaData, Table,
    Text, text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

metadata = MetaData()

_EMPTY = text("'{}'::jsonb")


def _when(name: str, nullable: bool = False) -> Column[datetime]:
    return Column(name, TIMESTAMP(timezone=True), nullable=nullable)


accounts = Table(
    "accounts", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    _when("created_at"),
    _when("last_seen_at"),
    Column("presentation", JSONB, nullable=False, server_default=_EMPTY),
    # Recovery words, only as "s1$" + scrypt (accounts/words.py): unique, since the words alone find their account.
    Column("words_hash", LargeBinary, nullable=True, unique=True),
    _when("words_made_at", nullable=True),
    # The player's lessons setting: on until they turn lessons off for every game of the account.
    Column("lessons", Boolean, nullable=False, server_default=text("true")),
    Index("ix_accounts_last_seen_at", "last_seen_at"),
)

# A transfer code, only as "h1$" + its HMAC under ASHFALL_JOIN_KEY (accounts/codes.py). Deleted when used, replaced by
# the account's next, or swept a batch at a time once expired by whoever makes the next code.
transfer_codes = Table(
    "transfer_codes", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("account_id", BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("code_hash", LargeBinary, nullable=False, unique=True),
    _when("created_at"),
    _when("expires_at"),
    Index("ix_transfer_codes_account_id", "account_id"),
    Index("ix_transfer_codes_expires_at", "expires_at"),
)

sessions = Table(
    "sessions", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("account_id", BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("token_hash", LargeBinary, nullable=False, unique=True),
    _when("created_at"),
    _when("last_seen_at"),
    Column("label", Text, nullable=True),
    Index("ix_sessions_account_id", "account_id"),
)

# A save outlives a session, so deleting an account with saves is refused rather than cascaded: a device join moves
# them first (docs/decisions.md, "A plain browser game"). Deleting a save is `deleted_at`; the row is deleted for good
# once it has been held long enough (saves/games.py).
saves = Table(
    "saves", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("account_id", BigInteger, ForeignKey("accounts.id"), nullable=False),
    _when("created_at"),
    _when("started_at"),
    _when("updated_at"),
    Column("state", Text, nullable=False),
    Column("format", Integer, nullable=False),
    Column("rules_digest", Text, nullable=False),
    Column("decisions", Integer, nullable=False),
    Column("game_time", BigInteger, nullable=False),
    Column("ended_at", BigInteger, nullable=True),
    _when("deleted_at", nullable=True),
    # The build that last wrote the save, and the content release it wrote it under (the release lock's number): a pod
    # of an earlier release must not write over it.
    Column("build", Text, nullable=True),
    Column("release", Integer, nullable=True),
    # The save's number among its account's games (null: begun by a build before numbers, until next written), and
    # the Camp levels it had landed when last written (null: not written since a build that keeps it).
    Column("number", Integer, nullable=True),
    Column("camp_level", Integer, nullable=True),
    # What the rules did lately (saves/ruleruns.py): null until a write of a build that keeps it.
    Column("rule_runs", JSONB, nullable=True),
    # What the page keeps about this save's teaching (api/CONTRACT.txt, SavePresentation): it only grows.
    Column("presentation", JSONB, nullable=False, server_default=_EMPTY),
    Index("ix_saves_account_id", "account_id"),
    Index("ix_saves_deleted_at", "deleted_at", postgresql_where=text("deleted_at IS NOT NULL")),
)

save_lines = Table(
    "save_lines", metadata,
    Column("save_id", BigInteger, ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True),
    Column("n", Integer, primary_key=True),
    Column("at", BigInteger, nullable=False),
    Column("key", Text, nullable=False),
)

save_decisions = Table(
    "save_decisions", metadata,
    Column("save_id", BigInteger, ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True),
    Column("n", Integer, primary_key=True),
    Column("at", BigInteger, nullable=False),
    _when("wall"),
    Column("kind", Text, nullable=False),
    Column("verb", JSONB, nullable=False),
    Column("rules_digest", Text, nullable=False),
    Column("context", JSONB, nullable=True),
    Index("ix_save_decisions_save_id_kind_at", "save_id", "kind", "at"),
)

save_snapshots = Table(
    "save_snapshots", metadata,
    Column("save_id", BigInteger, ForeignKey("saves.id", ondelete="CASCADE"), primary_key=True),
    Column("day", Integer, primary_key=True),
    Column("state", Text, nullable=False),
    Column("rules_digest", Text, nullable=False),
    Column("decisions", Integer, nullable=False),
)

# The manifest (engine DESIGN.txt, "Manifest") of each rules digest a build has played under, as canonical JSON text: a
# save or snapshot whose state leaves its manifest out is read with its digest's (db/manifests.py).
save_manifests = Table(
    "save_manifests", metadata,
    Column("rules_digest", Text, primary_key=True),
    Column("manifest", Text, nullable=False),
)

# One row per counted request. `who` is an HMAC-SHA256 of the client address under ASHFALL_RATE_KEY (never the
# address), an account's id, or one constant for a count across everyone; each kind's writer prunes its rows past the
# longest window it counts.
tries = Table(
    "tries", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("kind", Text, nullable=False),
    Column("who", LargeBinary, nullable=False),
    _when("at"),
    Index("ix_tries_kind_who_at", "kind", "who", "at"),
)

# What testers sent from the page (feedback/), read back by the owner (python -m ashfall_app.feedback). `account_id` and
# `save_id` are plain ids, not keys: the account may be pruned or the save deleted and the words stay. `last_line` is
# the internal text key of the save's newest log line. The writer deletes rows past its retention on insert.
feedback = Table(
    "feedback", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    _when("created_at"),
    Column("text", Text, nullable=False),
    Column("build", Text, nullable=False),
    Column("release", Integer, nullable=False),
    Column("account_id", BigInteger, nullable=True),
    Column("save_id", BigInteger, nullable=True),
    Column("game_time", BigInteger, nullable=True),
    Column("last_line", Text, nullable=True),
    Index("ix_feedback_created_at", "created_at"),
)

# A device with reminders on (reminders/); no row is off. `visited_at` is the player's last visit, `last_sent_at` the
# claim that sent this absence's one reminder (db/reminders.py). Rows whose visit is over 180 days old are deleted by the
# job that sends.
reminder_devices = Table(
    "reminder_devices", metadata,
    Column("id", BigInteger, Identity(always=True), primary_key=True),
    Column("account_id", BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("endpoint", Text, nullable=False, unique=True),
    Column("p256dh", Text, nullable=False),
    Column("auth", Text, nullable=False),
    Column("after_hours", Integer, nullable=False),
    Column("tz", Text, nullable=False),
    Column("send_from_hour", Integer, nullable=False),
    Column("send_until_hour", Integer, nullable=False),
    _when("visited_at"),
    _when("last_sent_at", nullable=True),
    _when("created_at"),
    CheckConstraint("send_from_hour BETWEEN 0 AND 23 AND send_until_hour BETWEEN 0 AND 23",
                    name="ck_reminder_devices_send_hours"),
    Index("ix_reminder_devices_account_id", "account_id"),
    Index("ix_reminder_devices_visited_at", "visited_at"),
)
