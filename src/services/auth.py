from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from passlib.context import CryptContext
import jwt
import phonenumbers
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from random import randint
from password_strength import PasswordPolicy

from src.config import settings
from src.init import redis_manager

phone_code_storage = {}


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self):
        self.redis = redis_manager

    async def normalize_russian_phone(self, phone: str) -> str:
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("8") and len(phone) == 11:
            return "+7" + phone[1:]
        return phone

    async def validate_russian_phone(self, phone: str) -> PhoneNumber:
        try:
            phone = await self.normalize_russian_phone(phone)
            num = phonenumbers.parse(phone, "ru")
            return num
        except NumberParseException:
            raise NumberParseException

    async def test_send_sms(self, phone: str, code: int):
        print(f"[TEST SMS] Отправляем код {code} на номер {phone}")

    async def test_send_mail(self, email: EmailStr, code: int):
        print(f"[TEST MAIL] Отправляем код {code} на email {email}")

    async def generate_and_send_phone_code(self, phone: PhoneNumber, action: str):
        key_limit = f"rate_limit_{action}:{phone}"
        ttl = await redis_manager.redis.ttl(key_limit)
        if ttl > 0:
            raise HTTPException(
                status_code=429,
                detail=f"Отправить код снова вы можете не ранее, чем через {ttl} секунд.",
            )
        await redis_manager.set(key_limit, "1", expire=120)
        code = randint(1000, 9999)
        key = f"{action}:code:{phone}"
        await self.redis.set(key, code, expire=120)
        await self.test_send_sms(phone, code)
        return {"status": "Ok"}

    async def generate_and_send_email_code(self, email: EmailStr):
        key_limit = f"rate_limit_email:{email}"
        ttl = await redis_manager.redis.ttl(key_limit)
        if ttl > 0:
            raise HTTPException(
                status_code=429,
                detail=f"Отправить код снова вы можете не ранее, чем через {ttl} секунд.",
            )
        await redis_manager.set(key_limit, "1", expire=120)
        code = randint(1000, 9999)
        key = f"email:code:{email}"
        await self.redis.set(key, code, expire=120)
        await self.test_send_mail(email, code)
        return {"status": "Ok"}

    async def verify_code_phone(self, phone: PhoneNumber, code: int, action: str):
        key = f"{action}:code:{phone}"
        key_verified = f"{action}:code_verified:{phone}"
        stored_code = await self.redis.get(key)

        if not stored_code:
            raise HTTPException(status_code=400, detail="Код не найден или истёк")

        if int(stored_code) != code:
            raise HTTPException(status_code=400, detail="Неверный код")

        await self.redis.set(key_verified, "true", expire=300)
        return {"status": "Код подтверждён"}

    async def verify_code_email(self, email: EmailStr, code: int):
        key = f"email:code:{email}"
        key_verified = f"email:code_verified:{email}"
        stored_code = await self.redis.get(key)

        if not stored_code:
            raise HTTPException(status_code=400, detail="Код не найден или истёк")

        if int(stored_code) != code:
            raise HTTPException(status_code=400, detail="Неверный код подтверждения email")

        await self.redis.set(key_verified, "true", expire=300)
        return {"status": "Код подтверждён"}

    async def delete_verified_phone_code(self, phone: PhoneNumber, action: str):
        await self.redis.delete(f"{action}:code_verified:{phone}")
        await self.redis.delete(f"{action}:code:{phone}")

    async def delete_verified_email_code(self, email: EmailStr):
        await self.redis.delete(f"email:code_verified:{email}")
        await self.redis.delete(f"email:code:{email}")

    def validate_password_strength(self, password: str):
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
        )

        errors = policy.test(password)
        if errors:
            raise HTTPException(
                status_code=400,
                detail="Пароль должен быть не менее 8 символов, содержать цифру, заглавную букву и специальный символ",
            )

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_tokens(self, payload: dict):
        access_token = jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) + timedelta(days=7)},
            settings.JWT_REFRESH_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return access_token, refresh_token

    def create_access_token(self, payload: dict):
        return jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def decode_access_token(self, token: str):
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный access токен")

    def decode_refresh_token(self, token: str):
        try:
            return jwt.decode(
                token,
                settings.JWT_REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный refresh токен")
