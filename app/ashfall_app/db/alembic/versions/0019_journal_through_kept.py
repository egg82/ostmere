"""Every journal day carries the save time it was composed through: a day stored whole before revision 0015 (`through`
null) is a day closed at its end. Its notes stay in the order stored. The build before this one writes `through` on
every day and reads a closed day as stored, so it works on the new schema."""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None

DAY_S = 86_400


def upgrade() -> None:
    op.execute(sa.text("UPDATE save_journal SET through = (day + 1) * :day_s WHERE through IS NULL").bindparams(
        day_s=DAY_S))
    op.alter_column("save_journal", "through", existing_type=sa.BigInteger, nullable=False)


def downgrade() -> None:
    op.alter_column("save_journal", "through", existing_type=sa.BigInteger, nullable=True)
