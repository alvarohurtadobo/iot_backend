"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Crear tabla businesses
    op.create_table(
        'businesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('picture_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla users (sin foreign key a branches todavía por dependencia circular)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('profile_picture', sa.String(length=500), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Crear tabla branches
    op.create_table(
        'branches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('representative_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['representative_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_branches_business_id'), 'branches', ['business_id'], unique=False)
    
    # Agregar foreign key de users a branches después de crear branches
    op.create_foreign_key('fk_users_branch_id', 'users', 'branches', ['branch_id'], ['id'])
    
    # Crear tabla device_types
    op.create_table(
        'device_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_device_types_code'), 'device_types', ['code'], unique=False)
    
    # Crear tabla sensor_types
    op.create_table(
        'sensor_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_sensor_types_code'), 'sensor_types', ['code'], unique=False)
    
    # Crear tabla machines
    op.create_table(
        'machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_machines_branch_id'), 'machines', ['branch_id'], unique=False)
    op.create_index(op.f('ix_machines_business_id'), 'machines', ['business_id'], unique=False)
    op.create_index(op.f('ix_machines_code'), 'machines', ['code'], unique=False)
    
    # Crear tabla devices
    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.ForeignKeyConstraint(['type_id'], ['device_types.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_devices_machine_id'), 'devices', ['machine_id'], unique=False)
    op.create_index(op.f('ix_devices_type_id'), 'devices', ['type_id'], unique=False)
    op.create_index(op.f('ix_devices_code'), 'devices', ['code'], unique=False)
    
    # Crear tabla sensors
    op.create_table(
        'sensors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.ForeignKeyConstraint(['type_id'], ['sensor_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensors_device_id'), 'sensors', ['device_id'], unique=False)
    op.create_index(op.f('ix_sensors_machine_id'), 'sensors', ['machine_id'], unique=False)
    op.create_index(op.f('ix_sensors_type_id'), 'sensors', ['type_id'], unique=False)
    
    # Crear tabla time_data
    op.create_table(
        'time_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('sensor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_time_data_device_id'), 'time_data', ['device_id'], unique=False)
    op.create_index(op.f('ix_time_data_sensor_id'), 'time_data', ['sensor_id'], unique=False)
    op.create_index(op.f('ix_time_data_timestamp'), 'time_data', ['timestamp'], unique=False)
    op.create_index('idx_time_data_device_timestamp', 'time_data', ['device_id', 'timestamp'], unique=False)
    op.create_index('idx_time_data_sensor_timestamp', 'time_data', ['sensor_id', 'timestamp'], unique=False)
    
    # Crear tabla reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_branch_id'), 'reports', ['branch_id'], unique=False)
    op.create_index(op.f('ix_reports_business_id'), 'reports', ['business_id'], unique=False)
    op.create_index(op.f('ix_reports_device_id'), 'reports', ['device_id'], unique=False)
    op.create_index(op.f('ix_reports_machine_id'), 'reports', ['machine_id'], unique=False)
    
    # Crear tabla asociativa report_time_data
    op.create_table(
        'report_time_data',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('time_data_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
        sa.ForeignKeyConstraint(['time_data_id'], ['time_data.id'], ),
        sa.PrimaryKeyConstraint('report_id', 'time_data_id')
    )


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_table('report_time_data')
    op.drop_table('reports')
    op.drop_index('idx_time_data_sensor_timestamp', table_name='time_data')
    op.drop_index('idx_time_data_device_timestamp', table_name='time_data')
    op.drop_index(op.f('ix_time_data_timestamp'), table_name='time_data')
    op.drop_index(op.f('ix_time_data_sensor_id'), table_name='time_data')
    op.drop_index(op.f('ix_time_data_device_id'), table_name='time_data')
    op.drop_table('time_data')
    op.drop_index(op.f('ix_sensors_type_id'), table_name='sensors')
    op.drop_index(op.f('ix_sensors_machine_id'), table_name='sensors')
    op.drop_index(op.f('ix_sensors_device_id'), table_name='sensors')
    op.drop_table('sensors')
    op.drop_index(op.f('ix_devices_code'), table_name='devices')
    op.drop_index(op.f('ix_devices_type_id'), table_name='devices')
    op.drop_index(op.f('ix_devices_machine_id'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_machines_code'), table_name='machines')
    op.drop_index(op.f('ix_machines_business_id'), table_name='machines')
    op.drop_index(op.f('ix_machines_branch_id'), table_name='machines')
    op.drop_table('machines')
    op.drop_index(op.f('ix_sensor_types_code'), table_name='sensor_types')
    op.drop_table('sensor_types')
    op.drop_index(op.f('ix_device_types_code'), table_name='device_types')
    op.drop_table('device_types')
    op.drop_index(op.f('ix_branches_business_id'), table_name='branches')
    # Eliminar foreign key de users a branches antes de eliminar branches
    op.drop_constraint('fk_users_branch_id', 'users', type_='foreignkey')
    op.drop_table('branches')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('businesses')
    op.drop_table('roles')

