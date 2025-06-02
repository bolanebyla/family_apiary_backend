import sqlalchemy as sa

from family_apiary.products.infrastructure.database.meta import metadata

purchase_requests_table = sa.Table(
    'purchase_requests',
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
        'phone_number',
        sa.String,
        nullable=False,
        index=True,
    ),
    sa.Column(
        'name',
        sa.String,
        nullable=False,
    ),
    comment='Заявки на покупку продукции',
)
