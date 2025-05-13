from typing import Annotated
from fastapi import Depends, Query, HTTPException, Request, Response
from pydantic import BaseModel
from jwt import ExpiredSignatureError, DecodeError

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


async def get_token(request: Request, response: Response) -> dict:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Access токен не найден")

    try:
        return AuthService().decode_access_token(access_token)
    except ExpiredSignatureError:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh токен не найден")
        try:
            payload = AuthService().decode_refresh_token(refresh_token)
            new_access_token = AuthService().create_access_token(payload)
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                samesite="lax",
                secure=False,
            )
            return payload  # ✅ возвращаем payload сразу
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh токен истёк")
        except DecodeError:
            raise HTTPException(status_code=401, detail="Невалидный refresh токен")

    except DecodeError:
        raise HTTPException(status_code=401, detail="Невалидный access токен")


def get_current_user_dp(dp: str):
    async def dependency(
        payload: dict = Depends(get_token),  # ✅ получаем уже готовый payload
    ):
        return payload[dp]
    return dependency



UserIdDep = Annotated[int, Depends(get_current_user_dp("id"))]
UserRoleDep = Annotated[bool, Depends(get_current_user_dp("is_super_user"))]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
