from sqlalchemy import String, Float, Enum, Unicode, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.connection import Base
import enum
from typing import Optional

class AccountType(str, enum.Enum):
    cash = "cash"
    credit = "credit"
    investment = "investment"
    savings = "savings"
    other = "other"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType), default=AccountType.cash)
    emoji: Mapped[str] = mapped_column(Unicode(10), default="💰")
    color: Mapped[str] = mapped_column(String(20), default="#7c6aff")
    initial_balance: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)

    transactions_from: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="Transaction.account_id", back_populates="account"
    )
    transactions_to: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account"
    )
