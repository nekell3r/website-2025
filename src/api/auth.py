import sys

from fastapi import APIRouter, Body, Response, HTTPException, Request
from pathlib import Path

from src.api.dependencies import UserIdDep, DBDep
from src.init import redis_manager
from src.schemas.users import (
    UserAdd,
    UserRequestAdd,
    UserLogin,
    PhoneInput,
    PhoneWithCode,
    EmailInput,
    PhoneWithPassword,
    UserWithHashedPassword,
    UserUpdate,
)
from src.services.auth import AuthService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/auth", tags=["Логин и аутентефикация"])
register = APIRouter(prefix="/auth/register", tags=["Регистрация"])
reset = APIRouter(prefix="/auth/reset", tags=["Сброс пароля"])


@register.post(
    "/send_phone_code", summary="Отправка кода подтверждения регистрации на телефон"
)
async def send_phone_code(
    data: PhoneInput = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "phone": "+79282017042",
                },
            }
        }
    )
):
    telephone = data.phone
    await AuthService().generate_and_send_phone_code(telephone, "register")
    return {"status": "Ok, code is sent"}


@register.post(
    "/send_email_code", summary="Отправка кода подтверждения регистрации на почту"
)
async def send_email_code(
    data: EmailInput = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "email": "pashka@gmail.com",
                },
            }
        }
    )
):
    email = data.email
    await AuthService().generate_and_send_email_code(email)
    return {"status": "Ok"}


@register.post(
    "/verify",
    summary="Регистрация пользователя",
    description="Используется на странице регистрации"
    "Первичная регистрация пользователя и добавление данных в бд - если зарегистрирован, упадет 500 ошибка(скоро изменю на кастомную с описанием)",
)
async def verify_register(
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {
                    "telephone": "+79282017042",
                    "email": "pashka@gmail.com",
                    "code_phone": 0,
                    "code_email": 0,
                    "password": "my_password_pashka",
                    "password_repeat": "my_password_pashka",
                },
            }
        }
    ),
):
    key_phone = f"register:code:{data.telephone}"
    try:
        code_in_redis = int(await redis_manager.get(key_phone))
    except:
        raise HTTPException(
            404, detail="Код для этого номера не существует, отправьте заново"
        )
    if code_in_redis != data.code_phone:
        raise HTTPException(400, detail="Неверный код подтверждения по телефону")

    if data.email:
        key_email = f"email:code:{data.email}"
        try:
            email_code_in_redis = int(await redis_manager.get(key_email))
        except:
            raise HTTPException(
                404, detail="Код для этого email не существует, отправьте заново"
            )
        if email_code_in_redis != data.code_email:
            raise HTTPException(400, detail="Неверный код подтверждения по email")

    existing_user = await db.users.get_one_or_none(telephone=data.telephone)
    if existing_user:
        raise HTTPException(409, detail="Пользователь уже зарегистрирован")

    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(**data.model_dump(), hashed_password=hashed_password)
    await db.users.add(new_user_data)
    await db.commit()

    await redis_manager.delete(key_phone)
    if data.email:
        await redis_manager.delete(key_email)

    return {"status": "Ok, пользователь успешно зарегистрирован"}


@reset.post(
    "/send_code",
    summary="Отправка кода верификации",
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
            }
        }
    ),
):
    phone = data.phone
    user = await db.users.get_one_or_none(telephone=phone)
    if user is None:
        raise HTTPException(
            400, detail="Пользователь с таким телефоном не зарегистрирован в системе"
        )
    await AuthService().generate_and_send_phone_code(phone, "refresh")
    return {"status": "Ok"}


@reset.post("/verify", summary="проверка кода верификации")
async def verify_code(
    db: DBDep,
    data: PhoneWithCode = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {"phone": "+79282017042", "code": 9999},
            }
        },
    ),
):
    phone = data.phone
    code = data.code
    user = await db.users.get_one_or_none(telephone=phone)
    if user is None:
        raise HTTPException(
            400, detail="Пользователь с таким телефоном не зарегистрирован в системе"
        )
    await AuthService().verify_code_phone(phone, code, "refresh")
    return {"status": "OK, verification code is correct"}


@reset.post("/set_password", summary="Установка нового пароля")
async def set_password(
    db: DBDep,
    data: PhoneWithPassword = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "phone": "+79282017042",
                    "password": "12345678",
                    "password_repeat": "12345678",
                },
            }
        },
    ),
):
    is_verified = await redis_manager.get(f"reset_verified:{data.phone}")
    if not is_verified:
        raise HTTPException(403, detail="Код не подтверждён или устарел")
    if data.password != data.password_repeat:
        raise HTTPException(400, detail="Пароли не совпадают")

    user = await db.users.get_one_or_none(telephone=data.phone)
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")

    hashed_password = AuthService().hash_password(data.password)
    await db.users.edit(
        UserWithHashedPassword(**user.model_dump(), hashed_password=hashed_password),
        telephone=data.phone,
    )
    await db.commit()
    await redis_manager.delete(f"reset_verified:{data.phone}")


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
                    "telephone": "+79282017042",
                    "password": "my_password_pashka",
                },
            }
        }
    ),
):
    user = await db.users.get_user_with_hashed_password(phone=data.telephone)
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


@router.post("/update", summary="Изменение данных о пользователе")
async def update_data(
    db: DBDep,
    user_id: UserIdDep,
    new_data: UserUpdate = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {"name": "Павел", "surname": "Жабский", "grade": 11},
            }
        }
    ),
):
    user = await db.users.get_one_or_none(id=user_id)
    if user is None:
        raise HTTPException(404, detail="Пользователь не найден")
    await db.users.edit(new_data, exclude_unset=True, telephone=user.telephone)
    await db.commit()
    return {"status": "Ok, данные обновлены"}


@router.get(
    "/me",
    summary="Получение данных о пользователе",
    description="Получение всех данных о пользователе в личном кабинете: купленные продукты, id, имя, телефон, почта, роль",
)
async def get_me(
    db: DBDep,
    user_id: UserIdDep,
):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.get(
    "/logout",
    summary="Выход из системы",
    description="Очищение куков, происходит автоматически при просрочке refresh токена или по нажатию кнопки логаута в личном кабинете",
)
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "ok, user is logged out"}
