"""Test databases on the Postgres server ASHFALL_TEST_PG names (CI's postgres service; locally a throwaway container).

The schema is migrated once per server and set of revisions into a template database, and each test that asks gets
its own copy (`CREATE DATABASE ... TEMPLATE`), so no two tests share rows and none pays for the migration."""

import hashlib
import uuid

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from ashfall_app.db.migrate import MIGRATE_LOCK, SCRIPTS, migrate


def with_db(url: str, name: str) -> str:
    return make_conninfo(url, dbname=name)


def scripts_key() -> str:
    files = sorted((SCRIPTS / "versions").glob("*.py"))
    return hashlib.sha256(b"\0".join(f.name.encode() + b"\0" + f.read_bytes() for f in files)).hexdigest()[:12]


def create(admin: str, template: str = "template0") -> str:
    """A new database, byte-sorted, copied from `template`; its URL."""
    name = "t_" + uuid.uuid4().hex[:16]
    with psycopg.connect(admin, autocommit=True) as c:
        c.execute(sql.SQL("CREATE DATABASE {} TEMPLATE {} ENCODING 'UTF8' LOCALE 'C'").format(
            sql.Identifier(name), sql.Identifier(template)))
    return with_db(admin, name)


def drop(url: str) -> None:
    name = conninfo_to_dict(url)["dbname"]
    with psycopg.connect(with_db(url, "postgres"), autocommit=True) as c:
        c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(str(name))))


def template(admin: str) -> str:
    """The migrated template for these revisions, built under the migrate lock and renamed into place only once whole,
    so a run that died halfway never leaves one to be copied."""
    name = "ashfall_tmpl_" + scripts_key()
    with psycopg.connect(admin, autocommit=True) as c:
        c.execute("SELECT pg_advisory_lock(%s)", (MIGRATE_LOCK,))
        try:
            if not c.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
                build = create(admin)
                migrate(build)
                c.execute(sql.SQL("ALTER DATABASE {} RENAME TO {}").format(
                    sql.Identifier(str(conninfo_to_dict(build)["dbname"])), sql.Identifier(name)))
        finally:
            c.execute("SELECT pg_advisory_unlock(%s)", (MIGRATE_LOCK,))
    return name
