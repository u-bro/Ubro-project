from sqlalchemy import Integer, String, TIMESTAMP, Boolean, func, DECIMAL, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base, metadata


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    inviter_id: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)

    created_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True, default=func.now())
    last_active_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True, default=func.now())

    balance: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False, default=400)
    balance_updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True, default=func.now())

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lang_code: Mapped[str | None] = mapped_column(String(5), nullable=True, default='EN')
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    user_phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    transactions = relationship("Transaction", back_populates="user")