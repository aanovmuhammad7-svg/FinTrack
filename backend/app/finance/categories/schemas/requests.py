from pydantic import BaseModel, Field
from typing import Literal

class CategoryCreateRequest(BaseModel):
    name: str = Field(..., max_length=100, description="Название категории")
    type: Literal["income", "expense"] = Field(..., description="Тип категории: доход или расход")


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=100, description="Новое название категории")
    type: Literal["income", "expense"] | None = Field(None, description="Новый тип категории")
