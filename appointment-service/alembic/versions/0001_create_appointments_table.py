"""create appointments table"""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_appointments_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Creates appointments table for appointment service."""
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("doctor_name", sa.String(length=100), nullable=False),
        sa.Column("appointment_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("booked_by", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_appointments_id", "appointments", ["id"], unique=False)
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"], unique=False)
    op.create_index("ix_appointments_booked_by", "appointments", ["booked_by"], unique=False)


def downgrade() -> None:
    """Drops appointments table for appointment service."""
    op.drop_index("ix_appointments_booked_by", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_index("ix_appointments_id", table_name="appointments")
    op.drop_table("appointments")
