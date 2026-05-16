from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AccountType(str, Enum):
    cash = "cash"
    credit = "credit"
    investment = "investment"
    savings = "savings"
    other = "other"


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: AccountType = AccountType.cash
    emoji: str = Field(default="💰", max_length=10)
    color: str = Field(default="#7c6aff", pattern=r"^#[0-9a-fA-F]{6}$")
    initial_balance: float = Field(default=0.0, ge=0)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[AccountType] = None
    emoji: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    initial_balance: Optional[float] = Field(None, ge=0)


class AccountOut(AccountBase):
    id: str
    current_balance: float = 0.0
    is_active: bool = True

    model_config = {"from_attributes": True}
