from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ProductsCatalog(BaseModel):
    asin: Optional['str'] = Field(
        default=None,
        description="ID for product"
    )

    title: Optional['str'] = Field(
        default=None,
        description='Product name'
    )

    imgUrl: Optional['str'] = Field(
        default=None,
        description='Product image'
    )

    productURL: Optional['str'] = Field(
        default=None,
        description='Product URL'
    )

    stars: Optional['float'] = Field(
        default=None,
        description='Product rating'
    )

    price: Optional['float'] = Field(
        default=None,
        description='Product price'
    )

    category_id: int = Field(
        default=None,
        description='Product category'
    )

