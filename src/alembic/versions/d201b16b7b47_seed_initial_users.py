"""seed_initial_users

Revision ID: d201b16b7b47
Revises: eadb267cce3f
Create Date: 2026-04-03 22:10:19.366550

"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d201b16b7b47"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_table = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("uid", sa.String),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("role", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        user_table,
        [
            {
                "uid": "999e4567-e89b-12d3-a456-426614174000",
                "name": "Guest User",
                "email": "guest@example.com",
                "password": sa.null,
                "role": "guest",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM users WHERE email IN ('guest@example.com')")
