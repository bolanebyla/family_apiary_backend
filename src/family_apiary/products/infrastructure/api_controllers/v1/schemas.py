from decimal import Decimal

from pydantic import BaseModel, Field


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

        name: str
        description: str
        price: Decimal = Field(
            ...,
            ge=1,
        )
        category: str
        count: int = Field(
            ...,
            ge=1,
        )
