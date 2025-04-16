from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=True)

    grade: Mapped[int] = mapped_column(Integer, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
