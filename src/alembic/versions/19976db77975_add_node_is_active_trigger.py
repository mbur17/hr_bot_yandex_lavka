"""add node is_active trigger

Revision ID: 19976db77975
Revises: 5f04c9a0e7df
Create Date: 2025-07-20 12:15:20.534007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19976db77975'
down_revision: Union[str, Sequence[str], None] = '5f04c9a0e7df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION update_buttons_is_active()
        RETURNS TRIGGER AS $$
        BEGIN
	        UPDATE button SET is_active=NEW.is_active
	        WHERE target_node_id = NEW.id;
	        RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER button_before_update
        BEFORE UPDATE ON node
        FOR EACH ROW
        WHEN (OLD.is_active IS DISTINCT FROM NEW.is_active)
        EXECUTE FUNCTION update_buttons_is_active();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS button_before_update ON node;")
    op.execute("DROP FUNCTION IF EXISTS update_buttons_is_active;")
