from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from src.database import Base


class ReviewsORM(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    user_id: Mapped[int] = mapped_column()
    exam: Mapped[str] = mapped_column(String(10))
    result: Mapped[int] = mapped_column()
    review: Mapped[str] = mapped_column(String(500))
