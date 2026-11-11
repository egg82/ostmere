"""Alembic's environment: the connection migrate.py opened, already inside the one transaction that holds the migrate
lock and runs every revision. There is no alembic.ini and no URL here; migrate.py is the only way in."""

from alembic import context

context.configure(connection=context.config.attributes["connection"])
with context.begin_transaction():
    context.run_migrations()
