from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    email: Mapped[str | None] = mapped_column()
    telephone: Mapped[str] = mapped_column(String(15))
    password: Mapped[str] = mapped_column(String(50))
    exam: Mapped[str] = mapped_column(String(10))
