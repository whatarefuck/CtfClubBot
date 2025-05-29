"""Set default points to 0

Revision ID: aeb9217bbbee
Revises: 2329ddeb561d
Create Date: 2025-05-29 02:28:49.866795
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeb9217bbbee'
down_revision: Union[str, None] = '2329ddeb561d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Устанавливаем default=0 и nullable=False для points в таблице users
    op.alter_column('users', 'points',
                    existing_type=sa.INTEGER(),
                    server_default='0',
                    nullable=False)


def downgrade() -> None:
    # Отменяем изменения: убираем default и возвращаем nullable=True
    op.alter_column('users', 'points',
                    existing_type=sa.INTEGER(),
                    server_default=None,
                    nullable=True)