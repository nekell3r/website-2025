from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime, timezone

from src.database import Base


class ReviewsOrm(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    last_edit_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    # name: Mapped[str] = mapped_column(String(25))
    exam: Mapped[str] = mapped_column()
    result: Mapped[int] = mapped_column()
    review: Mapped[str] = mapped_column()
