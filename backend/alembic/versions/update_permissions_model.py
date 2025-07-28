"""Update permissions model

Revision ID: update_permissions_model
Revises: add_user_permissions
Create Date: 2023-11-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_permissions_model'
down_revision = 'add_user_permissions'  # Points to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Import inspect to check if columns exist
    from sqlalchemy import inspect
    
    # Create permissions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            name VARCHAR(50) NOT NULL,
            PRIMARY KEY (name)
        )
    """)

    # Get inspector to check column existence
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('user_permission_association')]
    
    # Check if permission column exists
    if 'permission' in columns:
        # Rename permission column to permission_name and add foreign key constraint
        with op.batch_alter_table('user_permission_association') as batch_op:
            # First, add the new column if it doesn't exist
            if 'permission_name' not in columns:
                batch_op.add_column(sa.Column('permission_name', sa.String(length=50), nullable=True))
        
        # Now that the column exists, update it with data from the permission column
        op.execute("UPDATE user_permission_association SET permission_name = permission")
        
        # Continue with the rest of the migration
        with op.batch_alter_table('user_permission_association') as batch_op:
            # Make permission_name not nullable
            batch_op.alter_column('permission_name', existing_type=sa.String(length=50), nullable=False)
            
            # Drop the old column
            batch_op.drop_column('permission')
    elif 'permission_name' not in columns:
        # If permission doesn't exist but permission_name also doesn't exist, create permission_name
        with op.batch_alter_table('user_permission_association') as batch_op:
            batch_op.add_column(sa.Column('permission_name', sa.String(length=50), nullable=False))
    
    # Add foreign key constraint if it doesn't exist
    # Check if the foreign key already exists
    foreign_keys = inspector.get_foreign_keys('user_permission_association')
    fk_exists = any(fk.get('name') == 'fk_user_permission_permission_name' for fk in foreign_keys)
    
    if not fk_exists:
        with op.batch_alter_table('user_permission_association') as batch_op:
            batch_op.create_foreign_key(
                'fk_user_permission_permission_name',
                'permissions',
                ['permission_name'],
                ['name']
            )
    
    # Insert existing permissions from the enum into the permissions table
    from app.models.permission import PermissionEnum
    conn = op.get_bind()
    for permission in PermissionEnum:
        conn.execute(
            sa.text("INSERT INTO permissions (name) VALUES (:name)"),
            {"name": permission.value}
        )


def downgrade():
    # Import inspect to check if columns exist
    from sqlalchemy import inspect
    
    # Get inspector to check column existence
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('user_permission_association')]
    foreign_keys = inspector.get_foreign_keys('user_permission_association')
    
    # Check if foreign key exists before trying to drop it
    fk_exists = any(fk.get('name') == 'fk_user_permission_permission_name' for fk in foreign_keys)
    if fk_exists:
        with op.batch_alter_table('user_permission_association') as batch_op:
            batch_op.drop_constraint('fk_user_permission_permission_name', type_='foreignkey')
    
    # Check if permission_name column exists
    if 'permission_name' in columns:
        # Rename permission_name back to permission
        with op.batch_alter_table('user_permission_association') as batch_op:
            # First, add the old column back if it doesn't exist
            if 'permission' not in columns:
                batch_op.add_column(sa.Column('permission', sa.String(length=50), nullable=True))
        
        # Update the old column with data from permission_name
        op.execute("UPDATE user_permission_association SET permission = permission_name")
        
        # Continue with the rest of the migration
        with op.batch_alter_table('user_permission_association') as batch_op:
            # Make permission not nullable
            batch_op.alter_column('permission', existing_type=sa.String(length=50), nullable=False)
            
            # Drop the new column
            batch_op.drop_column('permission_name')
    
    # Check if permissions table exists before dropping it
    table_names = inspector.get_table_names()
    if 'permissions' in table_names:
        # Drop permissions table
        op.drop_table('permissions')