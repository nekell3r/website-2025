from src.repositories.products import ProductsRepository
from src.repositories.purchases import PurchasesRepository
from src.repositories.reviews import ReviewsRepository
from src.repositories.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.reviews = ReviewsRepository(self.session)
        self.products = ProductsRepository(self.session)
        self.purchases = PurchasesRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
