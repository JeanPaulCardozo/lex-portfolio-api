"""Modify result_type Column

Revision ID: 33a404bc0c09
Revises: e24444db352c
Create Date: 2026-09-29 11:45:40.661880

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "33a404bc0c09"
down_revision: Union[str, Sequence[str], None] = "e24444db352c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    case_result_type = postgresql.ENUM(
        "sentencia", "acuerdo", "archivo", "dictamen", "otro",
        name="case_result_type",
    )
    case_result_type.create(op.get_bind(), checkfirst=True)

    op.alter_column("Cases", "year", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "Cases",
        "result_type",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        type_=case_result_type,
        nullable=False,
        postgresql_using="'otro'::case_result_type",
    )
    op.alter_column("Cases", "outcome", existing_type=sa.VARCHAR(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("Cases", "outcome", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        "Cases",
        "result_type",
        existing_type=postgresql.ENUM(
            "sentencia", "acuerdo", "archivo", "dictamen", "otro",
            name="case_result_type",
        ),
        type_=postgresql.ARRAY(sa.VARCHAR()),
        nullable=True,
    )
    op.alter_column("Cases", "year", existing_type=sa.INTEGER(), nullable=True)

    postgresql.ENUM(name="case_result_type").drop(op.get_bind(), checkfirst=True)