"""Add user permissions

Revision ID: add_user_permissions
Revises: 
Create Date: 2023-11-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_permissions'
down_revision = '001_create_auth_tables'  # Updated to point to the auth tables migration
branch_labels = None
depends_on = None


def upgrade():
    # Create user_permission_association table
    op.create_table(
        'user_permission_association',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_name', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'permission_name')
    )
    
    # Create index for faster lookups
    op.create_index(
        'ix_user_permission_association_user_id',
        'user_permission_association',
        ['user_id']
    )


def downgrade():
    # Drop index
    op.drop_index('ix_user_permission_association_user_id', 'user_permission_association')
    
    # Drop table
    op.drop_table('user_permission_association')