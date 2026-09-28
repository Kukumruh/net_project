"""add unique constraints

Revision ID: 9da71d5bb7f9
Revises: 3c1d33be386c
Create Date: 2026-09-28 22:36:45.274218

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9da71d5bb7f9'
down_revision: Union[str, Sequence[str], None] = '3c1d33be386c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_unique_constraint(
        'uq_categories_name',
        'categories',
        ['name']
    )

    op.create_unique_constraint(
        'uq_category_keyword',
        'classification_keywords',
        ['category_id', 'keyword_or_example']
    )

    op.create_unique_constraint(
        'uq_priorities_name',
        'priorities',
        ['name']
    )

    op.create_unique_constraint(
        'uq_category_user_assignment',
        'responsible_assignments',
        ['category_id', 'user_id']
    )

    op.create_unique_constraint(
        'uq_role_permission',
        'role_permissions',
        ['role_id', 'action_code']
    )

    op.create_unique_constraint(
        'uq_roles_name',
        'roles',
        ['name']
    )

    op.create_unique_constraint(
        'uq_statuses_name',
        'statuses',
        ['name']
    )

    op.create_unique_constraint(
        'uq_system_settings_param_key',
        'system_settings',
        ['param_key']
    )

    op.create_unique_constraint(
        'uq_users_telegram_chat_id',
        'users',
        ['telegram_chat_id']
    )

    op.create_unique_constraint(
        'uq_users_email',
        'users',
        ['email']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'uq_users_email',
        'users',
        type_='unique'
    )

    op.drop_constraint(
        'uq_users_telegram_chat_id',
        'users',
        type_='unique'
    )

    op.drop_constraint(
        'uq_system_settings_param_key',
        'system_settings',
        type_='unique'
    )

    op.drop_constraint(
        'uq_statuses_name',
        'statuses',
        type_='unique'
    )

    op.drop_constraint(
        'uq_roles_name',
        'roles',
        type_='unique'
    )

    op.drop_constraint(
        'uq_role_permission',
        'role_permissions',
        type_='unique'
    )

    op.drop_constraint(
        'uq_category_user_assignment',
        'responsible_assignments',
        type_='unique'
    )

    op.drop_constraint(
        'uq_priorities_name',
        'priorities',
        type_='unique'
    )

    op.drop_constraint(
        'uq_category_keyword',
        'classification_keywords',
        type_='unique'
    )

    op.drop_constraint(
        'uq_categories_name',
        'categories',
        type_='unique'
    )