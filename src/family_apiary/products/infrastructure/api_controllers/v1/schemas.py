from decimal import Decimal

from pydantic import BaseModel, Field

from commons.entities.base import EntityId


class CreatePurchaseRequest(BaseModel):
    """
    Создание заявки на покупку продукции
    """

    phone_number: str = Field(
        ...,
        examples=['+79999999999'],
    )
    name: str
    products: list['CreatePurchaseRequestProduct'] = Field(
        default_factory=list,
    )

    class CreatePurchaseRequestProduct(BaseModel):
        """
        Продукт из заявки на покупку
        """

        id: EntityId
        name: str
        description: str
        price: Decimal = Field(
            ...,
            gt=1,
        )
        category: str
        count: int = Field(
            ...,
            gt=1,
        )
