import sys

from fastapi import APIRouter, Body, Response, HTTPException
from pathlib import Path

from src.api.dependencies import UserIdDep
from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.schemas.users import UserAdd, UserRequestAdd
from src.services.auth import AuthService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентефикация"])


@router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Первичная регистрация пользователя и добавление данных в бд - если зарегистрирован, упадет 500 ошибка(скоро изменю на кастомную с описанием)",
)
async def register_user(
    user_data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {
                    "email": "pashka@gmail.com",
                    "password": "my_password_pashka",
                },
            },
            "2": {
                "summary": "Пользователь 2",
                "value": {
                    "email": "katya@gmail.com",
                    "password": "my_password_katya",
                },
            },
        }
    )
):
    hashed_password = AuthService().hash_password(user_data.password)
    new_user_data = UserAdd(email=user_data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "OK, user is registered"}


@router.post(
    "/login",
    summary="Логин пользователя",
    description="Логин пользователя - если пароль не найден или пользователь не найден, будут возвращены ошибки 401 с описанием",
)
async def login_user(
    response: Response,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {
                    "email": "pashka@gmail.com",
                    "password": "my_password_pashka",
                },
            },
            "2": {
                "summary": "Пользователь 2",
                "value": {
                    "email": "katya@gmail.com",
                    "password": "my_password_katya",
                },
            },
        }
    ),
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(
            email=data.email
        )
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не зарегистрирован")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Введён неверный пароль")
    access_token = AuthService().create_access_token({"id": user.id})
    response.set_cookie("access_token", access_token)
    return {"status": "ok, user is logged in", "access_token": access_token}


@router.get(
    "/me",
    summary="Получение объекта пользователя",
    description="Получение словаря с данными об id и email пользователя",
)
async def get_me(
    user_id: UserIdDep,
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        return user


@router.get("/logout", summary="Выход из системы", description="Очищение куков")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"status": "ok, user is logged out"}
