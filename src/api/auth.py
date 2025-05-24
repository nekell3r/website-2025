import sys

from fastapi import APIRouter, Body, Response, HTTPException, Request
from pathlib import Path
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from src.dependencies.db import DBDep
from src.schemas.users import (
    UserLogin,
    PhoneInput,
    EmailInput,
    RegistrationInput,
    ResetCodeVerifyInput,
    SetNewPasswordAfterResetInput
)
from src.services.auth import AuthService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/auth", tags=["Логин и аутентефикация"])
register = APIRouter(prefix="/auth/register", tags=["Регистрация"])
reset = APIRouter(prefix="/auth/reset", tags=["Сброс пароля"])


@register.post(
    "/phone_code", summary="Отправка кода подтверждения регистрации на телефон"
)
async def send_phone_code(
    db: DBDep,
    data: PhoneInput = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "phone": "+79282017042",
                },
            },
            "2": {
                "summary": "number 2",
                "value": {
                    "phone": "+79876543210",
                },
            },
        }
    ),
):
    await AuthService().send_registration_phone_code(data=data, db=db)
    return {"status": "Ok, код отправлен"}


@register.post(
    "/email_code", summary="Отправка кода подтверждения регистрации на почту"
)
async def send_email_code(
    db: DBDep,
    data: EmailInput = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "email": "pashka@gmail.com",
                },
            }
        }
    ),
):
    await AuthService().send_registration_email_code(data=data, db=db)
    return {"status": "Ok, код отправлен"}


@register.post(
    "/verify",
    summary="Регистрация пользователя",
    description=(
        "Используется на странице регистрации. "
        "Первичная регистрация пользователя и добавление данных в БД. "
        "Если пользователь уже зарегистрирован — вернёт 409 ошибку."
    ),
)
async def verify_register(
    db: DBDep,
    data: RegistrationInput = Body(
        openapi_examples={
            "phone_only": {
                "summary": "Регистрация по телефону",
                "value": {
                    "phone": "+79282017042",
                    "code": "1234",
                    "password": "Test_password_123"
                },
            },
            "email_only": {
                "summary": "Регистрация по email",
                "value": {
                    "email": "pashka@gmail.com",
                    "code": "4321",
                    "password": "Test_password_12345"
                },
            },
        }
    ),
):
    await AuthService().verify_registration(data=data, db=db)
    return {"status": "Ok, пользователь успешно зарегистрирован"}

@reset.post(
    "",
    summary="Отправка кода подтверждения сброса пароля",
    description="Отправляет код проверки на указанный телефон, позволяет отправлять раз в минуту",
)
async def send_reset_code(
    db: DBDep,
    data: PhoneInput = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "phone": "+79282017042",
                },
            },
            "2": {
                "summary": "number 2",
                "value": {
                    "phone": "+79876543210",
                },
            },
        }
    ),
):
    await AuthService().send_reset_phone_code(data, db=db)
    return {"status": "Ok, код сброса пароля отправлен"}


@reset.post("/verify", summary="Проверка кода верификации для сброса пароля")
async def verify_reset_code(
    db: DBDep,
    data: ResetCodeVerifyInput = Body(
        openapi_examples={
            "phone_code_verify": {
                "summary": "Верификация по телефону",
                "value": {
                    "phone": "+79282017042",
                    "code": "1234"
                },
            },
            "email_code_verify": {
                "summary": "Верификация по email",
                "value": {
                    "email": "pashka@gmail.com",
                    "code": "4321"
                },
            },
        },
    ),
):
    await AuthService().verify_reset(data=data, db=db)
    return {"status": "OK, verification code is correct"}


@reset.post("/password", summary="Установка нового пароля после сброса")
async def set_new_password_after_reset(
    db: DBDep,
    data: SetNewPasswordAfterResetInput = Body(
        openapi_examples={
            "phone_set_new_pass": {
                "summary": "Новый пароль по телефону",
                "value": {
                    "phone": "+79282017042",
                    "new_password": "NewStrongPassword1!",
                },
            },
            "email_set_new_pass": {
                "summary": "Новый пароль по email",
                "value": {
                    "email": "pashka@gmail.com",
                    "new_password": "AnotherNewStrongPassword1!",
                },
            },
        },
    ),
):
    await AuthService().set_password_after_reset(data=data, db=db)
    return {"status": "Ok, пароль изменён"}


@router.post(
    "/login",
    summary="Логин пользователя",
    description="Используется на странице логина"
    "Логин пользователя - если пароль не найден или пользователь не найден, будут возвращены ошибки 401 с описанием",
)
async def login_user(
    db: DBDep,
    response: Response,
    data: UserLogin = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {
                    "phone": "+79282017042",
                    "password": "Test_password_123",
                },
            },
            "2": {
                "summary": "Пользователь 2",
                "value": {
                    "phone": "+79876543210",
                    "password": "Test_password_12345",
                },
            },
        }
    ),
):
    try:
        phone_str_to_search = str(data.phone) 
        parsed_num = phonenumbers.parse(phone_str_to_search, None)
        if not phonenumbers.is_valid_number(parsed_num):
            raise HTTPException(status_code=400, detail="Неверный формат номера телефона для логина.")
        
        phone_e164_for_search = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        print(f"DEBUG (login_user API): Ищем пользователя по нормализованному номеру: {phone_e164_for_search}")
    except NumberParseException:
        raise HTTPException(status_code=400, detail="Неверный формат номера телефона при парсинге для логина.")

    user = await db.users.get_user_with_hashed_password(phone=phone_e164_for_search)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не зарегистрирован")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Введён неверный пароль")

    payload = {"id": user.id, "is_super_user": user.is_super_user}

    access_token, refresh_token = AuthService().create_tokens(payload)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",  # заменить на strict в проде
        secure=False,  # заменить на True в проде
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",  # заменить на strict в проде
        secure=False,  # заменить на True в проде
    )

    return {"status": "ok, user is logged in"}


@router.post(
    "/refresh",
    summary="Обновление access-токена",
    description="Обновление access-токена с использованием refresh-токена."
    "Необходимо выполнять запрос сюда при поимке 401 ошибки на фронте.",
)
async def refresh_token(request: Request, response: Response):
    refr_token = request.cookies.get("refresh_token")
    if not refr_token:
        raise HTTPException(401, detail="Не предоставлен refresh токен")

    payload = AuthService().decode_refresh_token(refr_token)
    try:
        new_access_token = AuthService().create_access_token(payload=payload)
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            samesite="lax",  # изменить на 'strict' в проде
            secure=False,  # включить True для HTTPS
        )
        return {"status": "Ok, access-token is updated"}
    except HTTPException:
        raise HTTPException(401, detail="Ошибка декодирования refresh-токена")


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Очищение куков, происходит автоматически при просрочке refresh токена или по нажатию кнопки логаута в личном кабинете",
)
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "ok, user is logged out"}
