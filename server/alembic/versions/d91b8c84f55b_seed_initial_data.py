"""Seed initial data

Revision ID: d91b8c84f55b
Revises: 733437e37956
Create Date: 2026-11-26 18:20:34.536974

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'd91b8c84f55b'
down_revision: str | Sequence[str] | None = '733437e37956'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
