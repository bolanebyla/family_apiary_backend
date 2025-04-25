from decimal import Decimal

from pydantic import BaseModel, Field

from commons.entities.base import EntityId


class CreateProductPurchaseRequest(BaseModel):
    """
    Создание заявки на покупку продукции
    """

    phone_number: str
    name: str
    products: list['CreateProductPurchaseRequestCommandProduct'] = Field(
        default_factory=list,
    )

    class CreateProductPurchaseRequestCommandProduct(BaseModel):
        """
        Продукт из заявки на покупку
        """

        id: EntityId
        name: str
        description: str
        price: Decimal
        category: str
        count: int = Field(
            ...,
            gt=1,
        )
