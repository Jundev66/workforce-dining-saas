"""initial_multitenant_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-11-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_slug'), 'tenants', ['slug'], unique=True)

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='admin'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_users_tenant_email')
    )
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # 3. Create employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('document_id', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=False, server_default='General'),
        sa.Column('position', sa.String(length=100), nullable=False, server_default='Employee'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('badge_code', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'document_id', name='uq_employees_tenant_doc'),
        sa.UniqueConstraint('tenant_id', 'badge_code', name='uq_employees_tenant_badge')
    )
    op.create_index(op.f('ix_employees_tenant_id'), 'employees', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_employees_document_id'), 'employees', ['document_id'], unique=False)
    op.create_index(op.f('ix_employees_department'), 'employees', ['department'], unique=False)
    op.create_index(op.f('ix_employees_status'), 'employees', ['status'], unique=False)
    op.create_index(op.f('ix_employees_badge_code'), 'employees', ['badge_code'], unique=False)

    # 4. Enable PostgreSQL Row-Level Security (RLS) for tenant isolation
    # Note: RLS allows granular row security based on app.current_tenant_id session variable
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY tenant_isolation_users ON users
        AS PERMISSIVE
        FOR ALL
        USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''))
        WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));
    """)

    op.execute("ALTER TABLE employees ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY tenant_isolation_employees ON employees
        AS PERMISSIVE
        FOR ALL
        USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''))
        WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), ''));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_employees ON employees;")
    op.execute("ALTER TABLE employees DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_users ON users;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")

    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('tenants')
