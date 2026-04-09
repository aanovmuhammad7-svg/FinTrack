from typing import Literal

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., max_length=100, description="Category name")
    type: Literal["income", "expense"] = Field(..., description="Category type")


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=100, description="New category name")
    type: Literal["income", "expense"] | None = Field(None, description="New category type")
