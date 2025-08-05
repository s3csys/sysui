"""Create auth tables

Revision ID: 001_create_auth_tables
Revises: 
Create Date: 2023-11-01

"""
from alembic import op
import sqlalchemy as sa

# Helper function to determine if we're using SQLite
def is_sqlite():
    return op.get_bind().engine.name == 'sqlite'

# Use Boolean for SQLite, TINYINT for MySQL
def get_boolean_type():
    if is_sqlite():
        return sa.Boolean()
    else:
        from sqlalchemy.dialects.mysql import TINYINT
        return TINYINT(1)


# revision identifiers, used by Alembic.
revision = '001_create_auth_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('is_active', get_boolean_type(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_verified', get_boolean_type(), nullable=False, server_default=sa.text('0')),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.Column('password_reset_token', sa.String(255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='viewer'),
        sa.Column('is_2fa_enabled', get_boolean_type(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create session table (renamed from refresh_tokens)
    op.create_table(
        'session',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.String(255), nullable=False, unique=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 can be up to 45 chars
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create totp_secret table for 2FA
    op.create_table(
        'totp_secret',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('is_verified', get_boolean_type(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create backup_code table for 2FA recovery
    op.create_table(
        'backup_code',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),  # Hashed backup code
        sa.Column('is_used', get_boolean_type(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_user_username', 'user', ['username'], unique=True)
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_index('ix_user_verification_token', 'user', ['verification_token'], unique=True)
    op.create_index('ix_user_password_reset_token', 'user', ['password_reset_token'], unique=True)
    op.create_index('ix_session_refresh_token', 'session', ['refresh_token'], unique=True)
    op.create_index('ix_session_user_id', 'session', ['user_id'])
    op.create_index('ix_backup_code_user_id', 'backup_code', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('backup_code')
    op.drop_table('totp_secret')
    op.drop_table('session')
    op.drop_table('user')