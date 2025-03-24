import sys

from fastapi import APIRouter, Body
from pathlib import Path
from sqlalchemy import insert

from src.database import async_session_maker
from src.models.users import UsersORM
from src.schemas.schemas import UserSchema

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(schema: UserSchema = Body()):
    async with async_session_maker() as session:
        statemant_add_user = insert(UsersORM).values(**schema.model_dump())
        await session.execute(statemant_add_user)
        await session.commit()
    return {"status": "OK, User created"}
