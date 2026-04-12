"""create patients table"""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_patients_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Creates patients table for patient service."""
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("condition", sa.String(length=200), nullable=False),
    )
    op.create_index("ix_patients_id", "patients", ["id"], unique=False)


def downgrade() -> None:
    """Drops patients table for patient service."""
    op.drop_index("ix_patients_id", table_name="patients")
    op.drop_table("patients")
