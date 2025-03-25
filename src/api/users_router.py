import sys

from fastapi import APIRouter, Body
from pathlib import Path
from sqlalchemy import insert, select

from src.database import async_session_maker
from src.models.users import UsersORM
from src.schemas.schemas import UserSchema
from src.database import engine

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users():
    async with async_session_maker() as session:
        query = select(UsersORM)
        result = await session.execute(query)
        users = result.scalars().all()
        return users


@router.post("/")
async def create_user(
    schema: UserSchema = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь Павла",
                "value": {
                    "name": "Павел",
                    "exam": "ЕГЭ",
                    "telephone": "+79999999999",
                },
            },
            "2": {
                "summary": "Пользователь Антона",
                "value": {"name": "Антон", "exam": "ОГЭ", "telephone": "+79999999999"},
            },
        }
    )
):
    async with async_session_maker() as session:
        add_user_stmt = insert(UsersORM).values(**schema.model_dump())
        print(add_user_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_user_stmt)
        await session.commit()
    return {"status": "OK, User created"}
