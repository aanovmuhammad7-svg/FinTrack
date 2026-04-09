from datetime import date, datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, Date, DateTime, String, Text, ForeignKey, Numeric, CheckConstraint, UniqueConstraint, func
from decimal import Decimal

from app.db.models.base import Base, IDMixin


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


    categories: Mapped[list["Category"]] = relationship("Category", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user", lazy="selectin")
    budgets: Mapped[list["Budget"]] = relationship("Budget", back_populates="user", cascade="all, delete-orphan", lazy="selectin")



class Category(Base, IDMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="categories", lazy="joined")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="category", lazy="selectin")
    budgets: Mapped[list["Budget"]] = relationship("Budget", back_populates="category", lazy="selectin")


class Budget(Base, IDMixin):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    limit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("limit_amount > 0", name="check_budget_limit_positive"),
        CheckConstraint("period_start <= period_end", name="check_budget_period_valid"),
        UniqueConstraint("user_id", "category_id", "period_start", "period_end", name="uq_budget_user_category_period"),
    )

    user: Mapped["User"] = relationship("User", back_populates="budgets", lazy="joined")
    category: Mapped["Category"] = relationship("Category", back_populates="budgets", lazy="joined")



class Transaction(Base, IDMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 🔒 Бизнес-инварианты
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions", lazy="joined")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions", lazy="joined")
