from datetime import date, datetime, timezone
#from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column #, relationship
from sqlalchemy import Integer, Boolean, Date, DateTime, String, Text #, Numeric, ForeignKey 

from app.db.models.base import Base, IDMixin


#class CategoryType(str, Enum):
#    income = "income"
#    expense = "expense"


class User(Base, IDMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),nullable=False)
    

    email_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    email_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)
    confirmation_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmation_token_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    password_reset_token: Mapped[Text | None] = mapped_column(Text, nullable=True)
    password_reset_token_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)
    last_password_reset: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    # relationships
    #categories = relationship("Category", back_populates="user")
    #transactions = relationship("Transaction", back_populates="user")
    #budgets = relationship("Budget", back_populates="user")

"""
class Categories(Base, IDMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[CategoryType] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),nullable=False,)

    # relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transactions(Base, IDMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"),nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    type: Mapped[CategoryType] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),nullable=False,)

    # relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Budgets(Base, IDMixin):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"),nullable=False)
    amount_limit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),nullable=False,)

    # relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
"""
