from sqlalchemy.orm import registry, relationship

from family_apiary.products.domain.entities import (
    PurchaseRequest,
    PurchaseRequestProduct,
)
from family_apiary.products.infrastructure.database.tables import (
    purchase_request_products_table,
    purchase_requests_table,
)

mapper = registry()

mapper.map_imperatively(
    PurchaseRequestProduct,
    purchase_request_products_table,
)

mapper.map_imperatively(
    PurchaseRequest,
    purchase_requests_table,
    properties={
        'products': relationship(
            'PurchaseRequestProduct',
        ),
    },
)
