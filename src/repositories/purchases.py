from sqlalchemy import update, select

from src.repositories.base import BaseRepository
from src.models.purchases import PaymentOrm
from src.repositories.mappers.mappers import PurchasesMapper
from src.schemas.payments import Purchase, PaymentWebhookData


class PurchasesRepository(BaseRepository):
    model = PaymentOrm
    schema = Purchase
    mapper = PurchasesMapper

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
    async def get_all_filtered(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]