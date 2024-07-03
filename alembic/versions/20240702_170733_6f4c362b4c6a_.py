"""empty message

Revision ID: 6f4c362b4c6a
Revises: 7f98613ff6b2
Create Date: 2024-07-02 17:07:33.938458

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f4c362b4c6a"
down_revision: str | None = "7f98613ff6b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "journal", sa.Column("transaction_datetime", sa.DateTime(timezone=True), nullable=False)
    )
    op.drop_column("journal", "transaction_date")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "journal", sa.Column("transaction_date", sa.DATE(), autoincrement=False, nullable=False)
    )
    op.drop_column("journal", "transaction_datetime")
    # ### end Alembic commands ###
