from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean

from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_super_user: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    name: Mapped[str] = mapped_column(String(100), nullable=True)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    grade: Mapped[int] = mapped_column(Integer, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    has_product_1: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_product_2: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_product_3: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_product_4: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_product_5: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
