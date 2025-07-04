"""Create purchase_requests tables

Revision ID: f1b9d92998f3
Revises:
Create Date: 2025-06-02 01:56:34.438817+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f1b9d92998f3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'purchase_requests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_requests')),
        comment='Заявки на покупку продукции',
    )
    op.create_index(
        op.f('ix_products_purchase_requests_created_at'),
        'purchase_requests',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_products_purchase_requests_phone_number'),
        'purchase_requests',
        ['phone_number'],
        unique=False,
    )
    op.create_index(
        op.f('ix_products_purchase_requests_updated_at'),
        'purchase_requests',
        ['updated_at'],
        unique=False,
    )
    op.create_table(
        'purchase_request_products',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('purchase_request_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('count', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ['purchase_request_id'],
            ['products.purchase_requests.id'],
            name=op.f(
                'fk_purchase_request_products_purchase_request_id_purchase_requests'
            ),
        ),
        sa.PrimaryKeyConstraint(
            'id', name=op.f('pk_purchase_request_products')
        ),
        comment='Заявки на покупку продукции',
    )
    op.create_index(
        op.f('ix_products_purchase_request_products_created_at'),
        'purchase_request_products',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_products_purchase_request_products_purchase_request_id'),
        'purchase_request_products',
        ['purchase_request_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_products_purchase_request_products_updated_at'),
        'purchase_request_products',
        ['updated_at'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f('ix_products_purchase_request_products_updated_at'),
        table_name='purchase_request_products',
    )
    op.drop_index(
        op.f('ix_products_purchase_request_products_purchase_request_id'),
        table_name='purchase_request_products',
    )
    op.drop_index(
        op.f('ix_products_purchase_request_products_created_at'),
        table_name='purchase_request_products',
    )
    op.drop_table('purchase_request_products')
    op.drop_index(
        op.f('ix_products_purchase_requests_updated_at'),
        table_name='purchase_requests',
    )
    op.drop_index(
        op.f('ix_products_purchase_requests_phone_number'),
        table_name='purchase_requests',
    )
    op.drop_index(
        op.f('ix_products_purchase_requests_created_at'),
        table_name='purchase_requests',
    )
    op.drop_table('purchase_requests')
    # ### end Alembic commands ###
