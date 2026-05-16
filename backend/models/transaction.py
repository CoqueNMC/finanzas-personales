from sqlalchemy import String, Float, Date, Enum, ForeignKey, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.connection import Base
from datetime import date, datetime
import enum
from typing import Optional

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    expense_tc = "expense_tc"
    transfer = "transfer"
    invest = "invest"
    withdraw = "withdraw"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    to_account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    account: Mapped["Account | None"] = relationship(
        "Account", foreign_keys=[account_id], back_populates="transactions_from"
    )
    to_account: Mapped["Account | None"] = relationship(
        "Account", foreign_keys=[to_account_id], back_populates="transactions_to"
    )
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="transactions"
    )
