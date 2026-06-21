"""add server_default to auth_provider

Revision ID: 1add54cdf040
Revises: 49f39526fbb7
Create Date: 2026-06-09 07:30:15.676272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1add54cdf040'
down_revision: Union[str, Sequence[str], None] = '49f39526fbb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'auth_provider',
        server_default='local'
    )

def downgrade() -> None:
    op.alter_column('users', 'auth_provider',
        server_default=None
    )
