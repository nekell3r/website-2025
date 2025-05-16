from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime,  JSON, ForeignKey
from datetime import datetime, timezone

from src.database import Base


class PaymentOrm(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_slug: Mapped[String] = mapped_column(ForeignKey("products.slug"), nullable=False)

    payment_id: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    fiscal_receipt_url: Mapped[str | None] = mapped_column(nullable=True)
    raw_webhook_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
