from typing import Annotated
from fastapi import Depends

from src.utils.db_manager import DBManager
from src.database import get_async_session_maker


async def get_db():
    session_maker = get_async_session_maker()
    async with DBManager(session_factory=session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
