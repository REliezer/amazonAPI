from pydantic import BaseModel, Field

class ProductsCategories(BaseModel):
    id: int = Field(
        description='Id category'
    )

    category_name: str = Field(
        description='Category name'
    )
