from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    exam: Mapped[str] = mapped_column(String(10))
    telephone: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(nullable=True)
