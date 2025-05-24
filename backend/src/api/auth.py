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
    SetNewPasswordAfterResetInput,
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
            "reg_phone_example_1": {
                "summary": "Пример 1 (регистрация, основной)",
                "value": {"phone": "+79011234561"},
            },
            "reg_phone_example_2": {
                "summary": "Пример 2 (регистрация, для смешанного)",
                "value": {"phone": "+79022345678"},
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
            "reg_email_example_1": {
                "summary": "Пример 1 (регистрация, для смешанного)",
                "value": {"email": "user.register@example.com"},
            },
            "reg_email_example_2": {
                "summary": "Пример 2 (регистрация, альтернативный)",
                "value": {"email": "another.reg@example.net"},
            },
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
            "phone_only_valid": {
                "summary": "Регистрация по телефону (валидный пример)",
                "description": "Email и email_code не предоставляются. Пароли совпадают.",
                "value": {
                    "phone": "+79011234561",
                    "password": "Password123!",
                    "password_repeat": "Password123!",
                    "phone_code": 1111,
                },
            },
            "phone_and_email_valid": {
                "summary": "Регистрация по телефону и email (валидный пример)",
                "description": "Предоставляются email и email_code. Пароли совпадают.",
                "value": {
                    "phone": "+79022345678",
                    "email": "user.register@example.com",
                    "password": "AnotherPassword456$",
                    "password_repeat": "AnotherPassword456$",
                    "phone_code": 2222,
                    "email_code": 3333,
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
            "send_code_for_phone_reset": {
                "summary": "Отправка кода для сброса по телефону",
                "value": {
                    "phone": "+79033456789",
                },
            }
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
            "phone_code_verify_for_reset": {
                "summary": "Верификация кода (сброс по телефону)",
                "value": {"phone": "+79033456789", "code": 1234},
            }
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
            "phone_set_new_pass_after_reset": {
                "summary": "Новый пароль (сброс по телефону)",
                "value": {
                    "phone": "+79033456789",
                    "new_password": "NewPassword123!",
                    "new_password_repeat": "NewPassword123!",
                },
            }
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
            "login_registered_user_1": {
                "summary": "Вход пользователя (из примера регистрации phone_only_valid)",
                "value": {
                    "phone": "+79011234561",
                    "password": "Password123!",
                },
            },
            "login_example_2": {
                "summary": "Вход пользователя (другой пример)",
                "value": {
                    "phone": "+79041234564",
                    "password": "LoginPassword2@",
                },
            },
        }
    ),
):
    try:
        phone_str_to_search = str(data.phone)
        parsed_num = phonenumbers.parse(phone_str_to_search, None)
        if not phonenumbers.is_valid_number(parsed_num):
            raise HTTPException(
                status_code=400, detail="Неверный формат номера телефона для логина."
            )

        phone_e164_for_search = phonenumbers.format_number(
            parsed_num, phonenumbers.PhoneNumberFormat.E164
        )
        print(
            f"DEBUG (login_user API): Ищем пользователя по нормализованному номеру: {phone_e164_for_search}"
        )
    except NumberParseException:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат номера телефона при парсинге для логина.",
        )

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
