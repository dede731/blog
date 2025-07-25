"""Add sensitive words model

Revision ID: 2bb1881d451d
Revises: 8dfb843105d4
Create Date: 2025-07-17 12:54:28.612713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bb1881d451d'
down_revision = '8dfb843105d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensitive_words',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('sensitive_words', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sensitive_words_word'), ['word'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sensitive_words', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sensitive_words_word'))

    op.drop_table('sensitive_words')
    # ### end Alembic commands ###
