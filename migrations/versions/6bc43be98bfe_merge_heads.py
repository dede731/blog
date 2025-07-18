"""merge_heads

Revision ID: 6bc43be98bfe
Revises: 2bb1881d451d, add_cover_image_to_posts
Create Date: 2025-07-17 13:22:26.860529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bc43be98bfe'
down_revision = ('2bb1881d451d', 'add_cover_image_to_posts')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
