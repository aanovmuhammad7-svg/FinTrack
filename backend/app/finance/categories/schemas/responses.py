from pydantic import BaseModel, ConfigDict
from typing import Literal

class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: Literal["income", "expense"]

    class Config:
        model_config = ConfigDict(from_attributes=True)


class CategoriesListResponse(BaseModel):
    categories: list[CategoryResponse]
