import sqlalchemy as sa
from sqlalchemy.types import Float

from family_apiary.products.infrastructure.database.meta import metadata

purchase_request_products_table = sa.Table(
    'purchase_request_products',
    metadata,
    sa.Column('id', sa.UUID, primary_key=True, nullable=False),
    sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
    ),
    sa.Column(
        'updated_at',
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
    ),
    sa.Column(
        'purchase_request_id',
        sa.UUID,
        sa.ForeignKey('purchase_requests.id'),
        index=True,
    ),
    sa.Column(
        'name',
        sa.String,
        nullable=False,
    ),
    sa.Column(
        'description',
        sa.String,
        nullable=False,
    ),
    sa.Column(
        'category',
        sa.String,
        nullable=False,
    ),
    sa.Column(
        'price',
        Float,  # TODO: использовать Decimal
        nullable=False,
    ),
    sa.Column(
        'count',
        sa.INTEGER,
        nullable=False,
    ),
    comment='Заявки на покупку продукции',
)
