"""Seed initial data

Revision ID: d91b8c84f55b
Revises: 733437e37956
Create Date: 2026-11-26 18:20:34.536974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd91b8c84f55b'
down_revision: Union[str, Sequence[str], None] = '733437e37956'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
