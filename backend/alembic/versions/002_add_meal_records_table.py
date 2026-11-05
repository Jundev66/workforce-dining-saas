"""add_meal_records_table

Revision ID: 002_dining
Revises: 001_initial
Create Date: 2026-11-05 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_dining'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'meal_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('employee_id', sa.String(length=36), nullable=False),
        sa.Column('meal_type', sa.String(length=30), nullable=False),
        sa.Column('badge_code', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='approved'),
        sa.Column('notes', sa.String(length=255), nullable=True),
        sa.Column('consumed_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_meal_records_tenant_date', 'meal_records', ['tenant_id', 'consumed_at'], unique=False)
    op.create_index('ix_meal_records_emp_type_date', 'meal_records', ['employee_id', 'meal_type', 'consumed_at'], unique=False)
    op.create_index(op.f('ix_meal_records_tenant_id'), 'meal_records', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_meal_records_employee_id'), 'meal_records', ['employee_id'], unique=False)
    op.create_index(op.f('ix_meal_records_meal_type'), 'meal_records', ['meal_type'], unique=False)

    # Enable RLS
    op.execute("ALTER TABLE meal_records ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY tenant_isolation_meal_records ON meal_records
        AS PERMISSIVE
        FOR ALL
        USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''))
        WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_meal_records ON meal_records;")
    op.execute("ALTER TABLE meal_records DISABLE ROW LEVEL SECURITY;")
    op.drop_table('meal_records')
