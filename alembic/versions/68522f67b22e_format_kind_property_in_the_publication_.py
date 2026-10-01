"""Format Kind property in the publication entity

Revision ID: 68522f67b22e
Revises: c0fdd6f72064
Create Date: 2026-10-01 14:07:19.012278

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68522f67b22e"
down_revision: Union[str, Sequence[str], None] = "c0fdd6f72064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'article' TO 'articulo'")
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'talk' TO 'ponencia'")
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'book' TO 'libro'")
    # 'podcast' stays the same: name and value already match


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'articulo' TO 'article'")
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'ponencia' TO 'talk'")
    op.execute("ALTER TYPE publication_kind_type RENAME VALUE 'libro' TO 'book'")
