"""v0.4.1

Revision ID: 773b6a901410
Revises: 
Create Date: 2022-08-30 18:52:32.163285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '773b6a901410'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('apartments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='apartments'
    )
    op.create_index(op.f('ix_apartments_apartments_id'), 'apartments', ['id'], unique=False, schema='apartments')
    op.create_index(op.f('ix_apartments_apartments_name'), 'apartments', ['name'], unique=False, schema='apartments')
    op.create_table('boxes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('size', sa.String(), nullable=False),
    sa.Column('essential', sa.Boolean(), nullable=True),
    sa.Column('warm', sa.Boolean(), nullable=True),
    sa.Column('liquid', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='box_packing'
    )
    op.create_table('countdowns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('venue', sa.String(length=256), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('cost', sa.Float(), nullable=False),
    sa.Column('attending', sa.Boolean(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='habits'
    )
    op.create_table('completed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('completed_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='habits'
    )
    op.create_table('habits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='habits'
    )
    op.create_table('journal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('feeling', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('portfolio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('add_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('complete_date', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('apt_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('value_bool', sa.Boolean(), nullable=True),
    sa.Column('value_str', sa.String(), nullable=True),
    sa.Column('value_int', sa.Integer(), nullable=True),
    sa.Column('value_float', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['apt_id'], ['apartments.apartments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='apartments'
    )
    op.create_index(op.f('ix_apartments_features_id'), 'features', ['id'], unique=False, schema='apartments')
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('box_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('essential', sa.Boolean(), nullable=False),
    sa.Column('warm', sa.Boolean(), nullable=False),
    sa.Column('liquid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['box_id'], ['box_packing.boxes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='box_packing'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('items', schema='box_packing')
    op.drop_index(op.f('ix_apartments_features_id'), table_name='features', schema='apartments')
    op.drop_table('features', schema='apartments')
    op.drop_table('tasks')
    op.drop_table('portfolio')
    op.drop_table('journal')
    op.drop_table('habits', schema='habits')
    op.drop_table('completed', schema='habits')
    op.drop_table('categories', schema='habits')
    op.drop_table('events')
    op.drop_table('countdowns')
    op.drop_table('boxes', schema='box_packing')
    op.drop_index(op.f('ix_apartments_apartments_name'), table_name='apartments', schema='apartments')
    op.drop_index(op.f('ix_apartments_apartments_id'), table_name='apartments', schema='apartments')
    op.drop_table('apartments', schema='apartments')
    # ### end Alembic commands ###
