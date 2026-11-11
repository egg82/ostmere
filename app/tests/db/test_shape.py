"""The migrated schema is the one the plan describes (SHAPE) and the one the app's queries use (tables.py)."""
import psycopg
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Column, MetaData, Table, Text, create_engine
from sqlalchemy.pool import NullPool

from ashfall_app.db import tables

WHEN, BIG, INT, TEXT, JSON, BYTES, BOOL = "timestamp with time zone", "bigint", "integer", "text", "jsonb", "bytea", "boolean"

# table -> its columns in order, as (name, type, nullable)
SHAPE: dict[str, list[tuple[str, str, bool]]] = {
    "accounts": [("id", BIG, False), ("created_at", WHEN, False), ("last_seen_at", WHEN, False),
                 ("presentation", JSON, False), ("words_hash", BYTES, True), ("words_made_at", WHEN, True),
                 ("lessons", BOOL, False)],
    "sessions": [("id", BIG, False), ("account_id", BIG, False), ("token_hash", BYTES, False),
                 ("created_at", WHEN, False), ("last_seen_at", WHEN, False), ("label", TEXT, True)],
    "saves": [("id", BIG, False), ("account_id", BIG, False), ("created_at", WHEN, False), ("started_at", WHEN, False),
              ("updated_at", WHEN, False), ("state", TEXT, False), ("format", INT, False),
              ("rules_digest", TEXT, False), ("decisions", INT, False), ("game_time", BIG, False),
              ("ended_at", BIG, True), ("deleted_at", WHEN, True),
              ("build", TEXT, True), ("release", INT, True), ("number", INT, True), ("camp_level", INT, True),
              ("rule_runs", JSON, True), ("presentation", JSON, False)],
    "save_lines": [("save_id", BIG, False), ("n", INT, False), ("at", BIG, False), ("key", TEXT, False)],
    "save_decisions": [("save_id", BIG, False), ("n", INT, False), ("at", BIG, False), ("wall", WHEN, False),
                       ("kind", TEXT, False), ("verb", JSON, False), ("rules_digest", TEXT, False),
                       ("context", JSON, True)],
    "save_snapshots": [("save_id", BIG, False), ("day", INT, False), ("state", TEXT, False),
                       ("rules_digest", TEXT, False), ("decisions", INT, False)],
    "save_manifests": [("rules_digest", TEXT, False), ("manifest", TEXT, False)],
    "tries": [("id", BIG, False), ("kind", TEXT, False), ("who", BYTES, False), ("at", WHEN, False)],
    "feedback": [("id", BIG, False), ("created_at", WHEN, False), ("text", TEXT, False), ("build", TEXT, False),
                 ("release", INT, False), ("account_id", BIG, True), ("save_id", BIG, True), ("game_time", BIG, True),
                 ("last_line", TEXT, True)],
    "transfer_codes": [("id", BIG, False), ("account_id", BIG, False), ("code_hash", BYTES, False),
                       ("created_at", WHEN, False), ("expires_at", WHEN, False)],
    "reminder_devices": [("id", BIG, False), ("account_id", BIG, False), ("endpoint", TEXT, False),
                         ("p256dh", TEXT, False), ("auth", TEXT, False), ("after_hours", INT, False),
                         ("tz", TEXT, False), ("send_from_hour", INT, False), ("send_until_hour", INT, False),
                         ("visited_at", WHEN, False), ("last_sent_at", WHEN, True), ("created_at", WHEN, False)],
}
KEYS = {"accounts": ["id"], "sessions": ["id"], "saves": ["id"], "save_lines": ["save_id", "n"],
        "save_decisions": ["save_id", "n"], "save_snapshots": ["save_id", "day"],
        "save_manifests": ["rules_digest"], "tries": ["id"],
        "feedback": ["id"], "transfer_codes": ["id"], "reminder_devices": ["id"]}


def columns(url: str) -> dict[str, list[tuple[str, str, bool]]]:
    with psycopg.connect(url) as c:
        rows = c.execute("SELECT table_name, column_name, data_type, is_nullable = 'YES' FROM information_schema.columns"
                         " WHERE table_schema = 'public' AND table_name <> 'alembic_version'"
                         " ORDER BY table_name, ordinal_position").fetchall()
    out: dict[str, list[tuple[str, str, bool]]] = {}
    for table, column, kind, nullable in rows:
        out.setdefault(table, []).append((column, kind, nullable))
    return out


def keys(url: str) -> dict[str, list[str]]:
    with psycopg.connect(url) as c:
        rows = c.execute("SELECT tc.table_name, k.column_name FROM information_schema.table_constraints tc"
                         " JOIN information_schema.key_column_usage k USING (constraint_schema, constraint_name)"
                         " WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'"
                         " AND tc.table_name <> 'alembic_version' ORDER BY tc.table_name, k.ordinal_position").fetchall()
    out: dict[str, list[str]] = {}
    for table, column in rows:
        out.setdefault(table, []).append(column)
    return out


def diffs(url: str, metadata: MetaData) -> list[object]:
    engine = create_engine("postgresql+psycopg://", creator=lambda: psycopg.connect(url), poolclass=NullPool)
    try:
        with engine.connect() as conn:
            ctx = MigrationContext.configure(conn, opts={"compare_type": True, "compare_server_default": True})
            return list(compare_metadata(ctx, metadata))
    finally:
        engine.dispose()


def test_every_table_has_the_planned_columns_and_keys(pg_url: str):
    assert columns(pg_url) == SHAPE
    assert keys(pg_url) == KEYS


def test_tables_py_matches_what_the_migrations_built(pg_url: str):
    assert diffs(pg_url, tables.metadata) == []


def test_a_tables_py_that_drifted_is_caught(pg_url: str):
    drifted = MetaData()
    for t in tables.metadata.sorted_tables:
        t.to_metadata(drifted)
    Table("accounts", drifted, Column("nickname", Text), extend_existing=True)
    assert [d for d in diffs(pg_url, drifted) if "nickname" in repr(d)]


def test_no_default_reads_the_database_clock(pg_url: str):
    with psycopg.connect(pg_url) as c:
        defaults = c.execute("SELECT table_name, column_name, column_default FROM information_schema.columns"
                             " WHERE table_schema = 'public' AND column_default IS NOT NULL").fetchall()
    assert defaults, "no defaults read: the probe saw nothing"
    clocks = [d for d in defaults if any(w in str(d[2]).lower() for w in ("now(", "current_", "clock_", "localtime"))]
    assert clocks == []


def test_the_database_sorts_text_by_byte(pg_url: str):
    with psycopg.connect(pg_url) as c:
        assert c.execute("SELECT 'B' < 'a', 'Z' < 'a'").fetchone() == (True, True)
