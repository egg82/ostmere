"""Moving an account to another device (expand only, so the build before this one runs on it unchanged): an account's
recovery words, stored only as their slow hash, and when they were made; and transfer codes, stored only as their
keyed hash, each with the account it joins and when it stops working."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("words_hash", sa.LargeBinary, nullable=True))
    op.add_column("accounts", sa.Column("words_made_at", TIMESTAMP(timezone=True), nullable=True))
    op.create_unique_constraint("accounts_words_hash_key", "accounts", ["words_hash"])
    op.create_table(
        "transfer_codes",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("account_id", sa.BigInteger, sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.LargeBinary, nullable=False, unique=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", TIMESTAMP(timezone=True), nullable=False))
    op.create_index("ix_transfer_codes_account_id", "transfer_codes", ["account_id"])
    op.create_index("ix_transfer_codes_expires_at", "transfer_codes", ["expires_at"])


def downgrade() -> None:
    op.drop_table("transfer_codes")
    op.drop_constraint("accounts_words_hash_key", "accounts")
    op.drop_column("accounts", "words_made_at")
    op.drop_column("accounts", "words_hash")
