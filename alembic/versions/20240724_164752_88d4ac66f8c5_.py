"""empty message

Revision ID: 88d4ac66f8c5
Revises: c87e5b91d661
Create Date: 2024-07-24 16:47:52.291837

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "88d4ac66f8c5"
down_revision: str | None = "c87e5b91d661"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(table_name="job", column_name="reserved_units", new_column_name="usage_value")
    op.drop_column("job", "units")


def downgrade() -> None:
    op.add_column(
        "job",
        sa.Column(
            "units", sa.BIGINT(), server_default=sa.text("0"), autoincrement=False, nullable=False
        ),
    )
    op.alter_column(table_name="job", column_name="usage_value", new_column_name="reserved_units")
