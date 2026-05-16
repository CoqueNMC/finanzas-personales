from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(default="📦", max_length=10)
    color: str = Field(default="#555555", pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    emoji: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryOut(CategoryBase):
    id: str
    transaction_count: int = 0

    model_config = {"from_attributes": True}
