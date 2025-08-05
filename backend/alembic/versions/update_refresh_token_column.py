"""Update refresh_token column length

Revision ID: update_refresh_token_column
Revises: update_permissions_table_schema
Create Date: 2023-11-15
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_refresh_token_column'
down_revision = 'update_permissions_table_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter the refresh_token column in the session table to increase its length
    op.alter_column('session', 'refresh_token',
                    existing_type=sa.String(255),
                    type_=sa.String(512),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert the column length back to 255
    op.alter_column('session', 'refresh_token',
                    existing_type=sa.String(512),
                    type_=sa.String(255),
                    existing_nullable=False)