"""change_device_state_from_float_to_string

Revision ID: ad4df8caa4931
Revises: 001
Create Date: 2025-11-23 20:24:33.748737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'ad4df8caa493'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if state column exists
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('devices')]
    
    if 'state' in columns:
        # If it exists, alter the type from Float to String
        op.alter_column('devices', 'state',
                       type_=sa.String(20),
                       existing_type=sa.Float(),
                       existing_nullable=True)
    else:
        # If it doesn't exist, add it as String
        op.add_column('devices',
                     sa.Column('state', sa.String(20), nullable=True))


def downgrade() -> None:
    # Revert the change: change from String to Float
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('devices')]
    
    if 'state' in columns:
        # Try to convert string values to float
        # If there are non-numeric values, this might fail
        op.alter_column('devices', 'state',
                       type_=sa.Float(),
                       existing_type=sa.String(20),
                       existing_nullable=True,
                       postgresql_using='NULL')  # Set NULL for non-numeric values

