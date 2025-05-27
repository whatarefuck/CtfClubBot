"""Add violation_recorded to Task

Revision ID: 2329ddeb561d
Revises: a823942ffa16
Create Date: 2025-05-27 22:30:01.633575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2329ddeb561d'
down_revision: Union[str, None] = 'a823942ffa16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новый столбец с дефолтом False,
    # чтобы в существующих записях сразу проставилось корректное значение.
    op.add_column(
        'tasks',
        sa.Column(
            'violation_recorded',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('FALSE')
        )
    )
    # После заполнения можно убрать дефолт, чтобы в будущем он не применялся автоматически.
    op.alter_column(
        'tasks',
        'violation_recorded',
        server_default=None
    )


def downgrade() -> None:
    # Откат: просто удаляем столбец
    op.drop_column('tasks', 'violation_recorded')
