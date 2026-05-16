from sqlalchemy import String, Unicode, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.connection import Base
from typing import Optional

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[str] = mapped_column(Unicode(10), default="📦")
    color: Mapped[str] = mapped_column(String(20), default="#555555")
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category"
    )
