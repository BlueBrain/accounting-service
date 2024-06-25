"""empty message

Revision ID: 63a1d1c101bd
Revises:
Create Date: 2024-06-24 12:46:27.297268

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63a1d1c101bd"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

queuemessagestatus_enum = sa.Enum("COMPLETED", "FAILED", name="queuemessagestatus")
servicetype_enum = sa.Enum("STORAGE", "SHORT_JOBS", "LONG_JOBS", name="servicetype")


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "queue_message",
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("queue_name", sa.String(), nullable=False),
        sa.Column("status", queuemessagestatus_enum, nullable=False),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("counter", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(
        op.f("ix_queue_message_created_at"), "queue_message", ["created_at"], unique=False
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vlab_id", sa.Uuid(), nullable=False),
        sa.Column("proj_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_proj_id"), "transactions", ["proj_id"], unique=False)
    op.create_index(op.f("ix_transactions_vlab_id"), "transactions", ["vlab_id"], unique=False)
    op.create_table(
        "usage",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("vlab_id", sa.Uuid(), nullable=False),
        sa.Column("proj_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column("service_type", servicetype_enum, nullable=False),
        sa.Column("service_subtype", sa.String(), nullable=True),
        sa.Column("units", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usage_created_at"), "usage", ["created_at"], unique=False)
    op.create_index(op.f("ix_usage_job_id"), "usage", ["job_id"], unique=False)
    op.create_index(op.f("ix_usage_proj_id"), "usage", ["proj_id"], unique=False)
    op.create_index(op.f("ix_usage_vlab_id"), "usage", ["vlab_id"], unique=False)
    op.create_table(
        "vlab_topup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vlab_id", sa.Uuid(), nullable=False),
        sa.Column("proj_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("stripe_event_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vlab_topup_created_at"), "vlab_topup", ["created_at"], unique=False)
    op.create_index(op.f("ix_vlab_topup_proj_id"), "vlab_topup", ["proj_id"], unique=False)
    op.create_index(op.f("ix_vlab_topup_vlab_id"), "vlab_topup", ["vlab_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_vlab_topup_vlab_id"), table_name="vlab_topup")
    op.drop_index(op.f("ix_vlab_topup_proj_id"), table_name="vlab_topup")
    op.drop_index(op.f("ix_vlab_topup_created_at"), table_name="vlab_topup")
    op.drop_table("vlab_topup")
    op.drop_index(op.f("ix_usage_vlab_id"), table_name="usage")
    op.drop_index(op.f("ix_usage_proj_id"), table_name="usage")
    op.drop_index(op.f("ix_usage_job_id"), table_name="usage")
    op.drop_index(op.f("ix_usage_created_at"), table_name="usage")
    op.drop_table("usage")
    op.drop_index(op.f("ix_transactions_vlab_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_proj_id"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_queue_message_created_at"), table_name="queue_message")
    op.drop_table("queue_message")
    # ### end Alembic commands ###
    queuemessagestatus_enum.drop(op.get_bind(), checkfirst=True)
    servicetype_enum.drop(op.get_bind(), checkfirst=True)
