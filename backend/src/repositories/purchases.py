from sqlalchemy import update

from src.exceptions.db_exceptions import PurchaseNotFoundException
from src.repositories.base import BaseRepository
from src.models.purchases import PaymentOrm
from src.repositories.mappers.mappers import PurchasesMapper
from src.schemas.payments import Purchase, PaymentWebhookData


class PurchasesRepository(BaseRepository):
    model = PaymentOrm
    schema = Purchase
    mapper = PurchasesMapper
    not_found_exception = PurchaseNotFoundException

    async def edit(
        self, data: PaymentWebhookData, exclude_unset: bool = True, **filter_by
    ) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(
                status=data.status,
                paid_at=data.paid_at,
                fiscal_receipt_url=str(data.fiscal_receipt_url),
            )
        )
        await self.session.execute(update_stmt)
