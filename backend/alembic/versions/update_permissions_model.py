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
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    
    # Rename permission column to permission_name and add foreign key constraint
    with op.batch_alter_table('user_permission_association') as batch_op:
        # First, add the new column
        batch_op.add_column(sa.Column('permission_name', sa.String(length=50), nullable=True))
    
    # Now that the column exists, update it with data from the permission column
    op.execute("UPDATE user_permission_association SET permission_name = permission")
    
    # Continue with the rest of the migration
    with op.batch_alter_table('user_permission_association') as batch_op:
        # Make permission_name not nullable
        # batch_op.alter_column('permission_name', nullable=False)
        batch_op.alter_column('permission_name', existing_type=sa.String(length=50), nullable=False)
        
        # Drop the old column
        batch_op.drop_column('permission')
        
        # Add foreign key constraint
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
    # Remove foreign key constraint and rename column back
    with op.batch_alter_table('user_permission_association') as batch_op:
        batch_op.drop_constraint('fk_user_permission_permission_name', type_='foreignkey')
        
        # Create a temporary column
        batch_op.add_column(sa.Column('permission', sa.String(length=50), nullable=True))
    
    # Copy data from permission_name to permission
    op.execute('UPDATE user_permission_association SET permission = permission_name')
    
    # Continue with the rest of the downgrade
    with op.batch_alter_table('user_permission_association') as batch_op:
        # Make permission not nullable
        # batch_op.alter_column('permission', nullable=False)
        batch_op.alter_column('permission', existing_type=sa.String(length=50), nullable=False)
        
        # Drop the new column
        batch_op.drop_column('permission_name')
    
    # Drop permissions table
    op.drop_table('permissions')