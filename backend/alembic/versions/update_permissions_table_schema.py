"""update permissions table schema

Revision ID: update_permissions_table_schema
Revises: 
Create Date: 2023-11-15

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import re

# revision identifiers, used by Alembic.
revision = 'update_permissions_table_schema'
down_revision = 'update_permissions_model'  # Points to the previous migration
branch_labels = None
depends_on = None

# Helper function to determine if we're using SQLite
def is_sqlite():
    return op.get_bind().engine.name == 'sqlite'


def upgrade():
    # SQLite doesn't support many ALTER TABLE operations directly
    # We need to use batch operations for SQLite
    
    # Step 1: Add id column to permissions table if it doesn't exist
    # Check if id column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('permissions')]
    
    if 'id' not in columns:
        with op.batch_alter_table('permissions') as batch_op:
            batch_op.add_column(sa.Column('id', sa.Integer(), nullable=True))
    
    # Update the id column with sequential values
    conn = op.get_bind()
    conn.execute(text("UPDATE permissions SET id = rowid"))
    
    # Make id not nullable
    with op.batch_alter_table('permissions') as batch_op:
        batch_op.alter_column('id', nullable=False)
    
    # Step 2: Add permission_id column to user_permission_association if it doesn't exist
    # Check if permission_id column already exists
    columns = [col['name'] for col in inspector.get_columns('user_permission_association')]
    
    if 'permission_id' not in columns:
        with op.batch_alter_table('user_permission_association') as batch_op:
            batch_op.add_column(sa.Column('permission_id', sa.Integer(), nullable=True))
    
    # Update permission_id based on permission_name
    conn.execute(text("""
        UPDATE user_permission_association 
        SET permission_id = (SELECT id FROM permissions WHERE name = user_permission_association.permission_name)
    """))
    
    # Make permission_id not nullable
    with op.batch_alter_table('user_permission_association') as batch_op:
        batch_op.alter_column('permission_id', nullable=False)
    
    # Step 3: Create new primary key for permissions table
    with op.batch_alter_table('permissions') as batch_op:
        # In SQLite, we don't need to explicitly drop the old primary key
        # Just create a new one
        batch_op.create_primary_key('pk_permissions', ['id'])
    
    # Step 4: Update primary key in user_permission_association
    with op.batch_alter_table('user_permission_association') as batch_op:
        # In SQLite, we don't need to explicitly drop the old primary key
        # Just create a new one
        batch_op.create_primary_key('pk_user_permission', ['user_id', 'permission_id'])


def downgrade():
    # SQLite doesn't support many ALTER TABLE operations directly
    # We need to use batch operations for SQLite
    
    # Step 1: Restore old primary key in user_permission_association
    with op.batch_alter_table('user_permission_association') as batch_op:
        # In SQLite, we don't need to explicitly drop the old primary key
        # Just create a new one
        batch_op.create_primary_key('pk_user_permission', ['user_id', 'permission_name'])
    
    # Step 2: Restore old primary key for permissions table
    with op.batch_alter_table('permissions') as batch_op:
        # In SQLite, we don't need to explicitly drop the old primary key
        # Just create a new one
        batch_op.create_primary_key('pk_permissions', ['name'])
    
    # Step 3: Drop permission_id column from user_permission_association
    with op.batch_alter_table('user_permission_association') as batch_op:
        batch_op.drop_column('permission_id')
    
    # Step 4: Drop id column from permissions table
    with op.batch_alter_table('permissions') as batch_op:
        batch_op.drop_column('id')