from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date as date_type
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"
    expense_tc = "expense_tc"
    transfer = "transfer"
    invest = "invest"
    withdraw = "withdraw"


class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    date: date_type
    type: TransactionType
    account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    category_id: Optional[str] = None


class TransactionCreate(TransactionBase):
    @model_validator(mode="after")
    def validate_accounts(self):
        needs_dest = self.type in (
            TransactionType.transfer,
            TransactionType.invest,
            TransactionType.withdraw,
        )
        if needs_dest and not self.to_account_id:
            raise ValueError(f"to_account_id es requerido para tipo '{self.type}'")
        return self


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[date_type] = None
    type: Optional[TransactionType] = None
    account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    category_id: Optional[str] = None


class TransactionOut(TransactionBase):
    id: str
    account_name: Optional[str] = None
    account_emoji: Optional[str] = None
    category_name: Optional[str] = None
    category_emoji: Optional[str] = None
    category_color: Optional[str] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
  search: Optional[str] = None
  type: Optional[TransactionType] = None
  account_id: Optional[str] = None
  category_id: Optional[str] = None
  date_from: Optional[date_type] = None
  date_to: Optional[date_type] = None
  page: int = Field(default=1, ge=1)
  page_size: int = Field(default=50, ge=1, le=200)
