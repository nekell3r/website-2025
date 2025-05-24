from datetime import datetime, timezone, timedelta

from fastapi import Request, Response
from passlib.context import CryptContext
import jwt
import phonenumbers
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from random import randint
from password_strength import PasswordPolicy
from jwt import ExpiredSignatureError, DecodeError

from src.dependencies.db import DBDep
from src.config import settings
from src.init import redis_manager
from src.schemas.users import (
    UserAdd, 
    PhoneInput, 
    EmailInput, 
    UserWithHashedPassword,
    CodeInput, 
    RegistrationInput, 
    ResetCodeVerifyInput,
    SetNewPasswordAfterResetInput,
    SetPasswordInput
)
from src.exceptions.db_exceptions import UserNotFoundException
from src.exceptions.service_exceptions import (
    AuthRateLimitServiceException,
    UserAlreadyExistsServiceException,
    UserNotFoundAuthServiceException,
    AuthCodeInvalidServiceException,
    AuthCodeExpiredServiceException,
    AuthPasswordsNotMatchServiceException,
    AuthCodeNotVerifiedServiceException,
    AuthPasswordTooWeakServiceException,
    AuthTokenMissingServiceException,
    AuthTokenExpiredServiceException,
    AuthTokenInvalidServiceException,
    MadRussianServiceException,
    RegistrationValidationServiceException,
    ResetPasswordValidationServiceException,
    IncorrectPasswordServiceException
)

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

    async def validate_russian_phone(self, phone: str) -> phonenumbers.PhoneNumber:
        try:
            normalized_phone_str = await self.normalize_russian_phone(phone)
            num = phonenumbers.parse(normalized_phone_str, "RU")
            if not phonenumbers.is_valid_number(num):
                raise NumberParseException(phonenumbers.PhoneNumberFormat.E164, "Invalid phone number for RU")
            return num
        except NumberParseException as e:
            raise AuthCodeInvalidServiceException(detail="Неверный формат номера телефона") from e

    async def test_send_sms(self, phone_e164: str, code: int):
        print(f"[TEST SMS] Отправляем код {code} на номер {phone_e164}")

    async def test_send_mail(self, email: EmailStr, code: int):
        print(f"[TEST MAIL] Отправляем код {code} на email {email}")

    async def send_phone_code(self, phone_obj: phonenumbers.PhoneNumber, action: str):
        phone_e164 = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
        key_limit = f"rate_limit_{action}:{phone_e164}"
        ttl = await self.redis.ttl(key_limit)
        if ttl > 0:
            raise AuthRateLimitServiceException(
                detail=f"Отправить код снова вы можете не ранее, чем через {ttl} секунд."
            )
        await self.redis.set(key_limit, "1", expire=120) # Это для rate limit
        
        code = randint(1000, 9999)
        # Ключ, по которому будет храниться код
        key_for_code = f"{action}:code:{phone_e164}" 
        
        # Исправленный вызов: (ключ, значение, время жизни)
        await self.redis.set(key_for_code, str(code), expire=120)
        
        await self.test_send_sms(phone_e164, code)
        return {"status": "Ok"}

    async def send_email_code(self, email: EmailStr, action: str):
        key_limit = f"rate_limit_{action}:{email}"
        ttl = await self.redis.ttl(key_limit)
        if ttl > 0:
            raise AuthRateLimitServiceException(
                detail=f"Отправить код снова вы можете не ранее, чем через {ttl} секунд."
            )
        await self.redis.set(key_limit, "1", expire=120)
        code = randint(1000, 9999)
        key = f"{action}:code:{email}"
        await self.redis.set(key, str(code), expire=120)
        await self.test_send_mail(email, code)
        return {"status": "Ok"}

    async def send_registration_email_code(self, data: EmailInput, db: DBDep):
        existing_user = await db.users.get_one_or_none(email=data.email)
        if existing_user:
            raise UserAlreadyExistsServiceException
        result = await self.send_email_code(data.email, action="registration")
        return result

    async def send_registration_phone_code(self, data: PhoneInput, db: DBDep):
        valid_phone_obj = await self.validate_russian_phone(data.phone)
        phone_e164 = phonenumbers.format_number(valid_phone_obj, phonenumbers.PhoneNumberFormat.E164)
        
        existing_user = await db.users.get_one_or_none(phone=phone_e164)
        
        if existing_user:
            raise UserAlreadyExistsServiceException
        
        result = await self.send_phone_code(valid_phone_obj, "registration")
        return result

    async def send_reset_phone_code(self, data: PhoneInput, db:DBDep):
        valid_phone_obj = await self.validate_russian_phone(data.phone)
        phone_e164 = phonenumbers.format_number(valid_phone_obj, phonenumbers.PhoneNumberFormat.E164)
        try:
            await db.users.get_one(phone=phone_e164)
        except UserNotFoundException:
            raise UserNotFoundAuthServiceException
        result = await self.send_phone_code(valid_phone_obj, "reset")
        return result

    async def verify_code_phone(self, phone_obj: phonenumbers.PhoneNumber, code_input: CodeInput, action: str):
        phone_e164 = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
        key = f"{action}:code:{phone_e164}"
        
        stored_code_value = await self.redis.get(key) 

        if not stored_code_value:
            raise AuthCodeExpiredServiceException(detail="Код подтверждения истек или не был найден.")
        
        stored_code_str = stored_code_value.decode('utf-8') if isinstance(stored_code_value, bytes) else str(stored_code_value)
        input_code_str = str(code_input.code)

        if stored_code_str != input_code_str:
            raise AuthCodeInvalidServiceException(detail="Неверный код подтверждения.")

        key_verified = f"{action}:code_verified:{phone_e164}"
        await self.redis.set(key_verified, "true", expire=300)
        return {"status": "Код подтверждён"}

    async def verify_code_email(self, email: EmailStr, code_input: CodeInput, action: str):
        key = f"{action}:code:{email}"
        key_verified = f"{action}:code_verified:{email}"
        stored_code_bytes = await self.redis.get(key)

        if not stored_code_bytes:
            raise AuthCodeExpiredServiceException

        if stored_code_bytes.decode() != str(code_input.code):
            raise AuthCodeInvalidServiceException

        await self.redis.set(key_verified, "true", expire=300)
        return {"status": "Код подтверждён"}

    async def verify_registration(self, data: RegistrationInput, db:DBDep):
        if not (data.phone or data.email):
            raise RegistrationValidationServiceException(detail="Укажите номер телефона или email для регистрации.")
        if data.phone and data.email:
            raise RegistrationValidationServiceException(detail="Укажите что-то одно для регистрации: телефон или email.")

        user_identifier_dict = {}
        valid_phone_obj = None
        verified_with_phone = False

        if data.phone:
            valid_phone_obj = await self.validate_russian_phone(data.phone)
            phone_e164 = phonenumbers.format_number(valid_phone_obj, phonenumbers.PhoneNumberFormat.E164)
            existing_user = await db.users.get_one_or_none(phone=phone_e164)
            if existing_user:
                raise UserAlreadyExistsServiceException(detail="Пользователь с таким телефоном уже существует.")
            
            try:
                await self.verify_code_phone(valid_phone_obj, CodeInput(code=data.code), "registration")
            except MadRussianServiceException as e:
                raise 
            
            user_identifier_dict["phone"] = PydanticPhoneNumber(phone_e164) 
            verified_with_phone = True
        
        if data.email:
            existing_user = await db.users.get_one_or_none(email=data.email)
            if existing_user:
                raise UserAlreadyExistsServiceException(detail="Пользователь с таким email уже существует.")
            await self.verify_code_email(data.email, CodeInput(code=data.code), "registration")
            user_identifier_dict["email"] = data.email

        self.validate_password_strength(data.password)
        hashed_password = self.hash_password(data.password)

        new_user_data_dict = {
            "hashed_password": hashed_password,
            **user_identifier_dict
        }

        new_user_schema = UserAdd(**new_user_data_dict)
        await db.users.add(new_user_schema)
        await db.commit()
        
        if verified_with_phone and valid_phone_obj:
            await self.delete_verified_phone_code(valid_phone_obj, "registration")
        if data.email:
            await self.delete_verified_email_code(data.email, "registration")
            
        return {"status": "OK, user created"}

    async def verify_reset(self, data: ResetCodeVerifyInput, db:DBDep):
        if not (data.phone or data.email):
            raise ResetPasswordValidationServiceException(detail="Укажите номер телефона или email для сброса пароля.")
        if data.phone and data.email:
            raise ResetPasswordValidationServiceException(detail="Укажите что-то одно для сброса: телефон или email.")

        user_found = False
        if data.phone:
            if data.phone is None:
                 raise ResetPasswordValidationServiceException(detail="Телефон не предоставлен для верификации кода сброса.")
            valid_phone_obj = await self.validate_russian_phone(str(data.phone))
            phone_e164 = phonenumbers.format_number(valid_phone_obj, phonenumbers.PhoneNumberFormat.E164)
            try:
                await db.users.get_one(phone=phone_e164)
                user_found = True
            except UserNotFoundException:
                pass
            
            if user_found:
                await self.verify_code_phone(valid_phone_obj, CodeInput(code=data.code), "reset")
                return {"status": "OK, verification code is correct for phone"}
        
        if data.email:
            if data.email is None:
                raise ResetPasswordValidationServiceException(detail="Email не предоставлен для верификации кода сброса.")
            try:
                await db.users.get_one(email=data.email)
                user_found = True
            except UserNotFoundException:
                pass

            if user_found:
                await self.verify_code_email(data.email, CodeInput(code=data.code), "reset")
                return {"status": "OK, verification code is correct for email"}
        
        if not user_found:
            raise UserNotFoundAuthServiceException(detail="Пользователь не найден.")
        
        raise MadRussianServiceException(detail="Не удалось верифицировать код сброса.") 

    async def delete_verified_phone_code(self, phone_obj: phonenumbers.PhoneNumber, action: str):
        phone_e164 = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
        key = f"{action}:code:{phone_e164}"
        key_verified = f"{action}:code_verified:{phone_e164}"
        await self.redis.delete(key)
        await self.redis.delete(key_verified)

    async def delete_verified_email_code(self, email: EmailStr, action: str):
        await self.redis.delete(f"{action}:code_verified:{email}")

    async def set_password_after_reset(self, data: SetNewPasswordAfterResetInput, db:DBDep):
        if not (data.phone or data.email):
            raise ResetPasswordValidationServiceException(detail="Укажите номер телефона или email.")

        if data.phone and data.email:
            raise ResetPasswordValidationServiceException(detail="Укажите что-то одно: телефон или email.") 

        identifier_type = "" 
        identifier_value = ""
        user_object_key = "" 
        valid_phone_obj: phonenumbers.PhoneNumber | None = None

        if data.phone:
            valid_phone_obj = await self.validate_russian_phone(data.phone)
            identifier_type = "phone"
            identifier_value = phonenumbers.format_number(valid_phone_obj, phonenumbers.PhoneNumberFormat.E164)
            user_object_key = "phone"
        elif data.email:
            identifier_type = "email"
            identifier_value = data.email
            user_object_key = "email"

        is_verified_key = f"reset:code_verified:{identifier_value}"
        is_verified_value = await self.redis.get(is_verified_key)
        
        is_verified_str = is_verified_value.decode('utf-8') if isinstance(is_verified_value, bytes) else str(is_verified_value)

        if not is_verified_value or is_verified_str != "true":
            raise AuthCodeNotVerifiedServiceException(detail="Код не был верифицирован или сессия истекла.")
        
        try:
            user = await db.users.get_one(**{user_object_key: identifier_value})
        except UserNotFoundException:
            raise UserNotFoundAuthServiceException(detail="Пользователь не найден.")
        
        self.validate_password_strength(data.new_password) 
        hashed_password = self.hash_password(data.new_password)
        
        await db.users.edit(id=user.id, data={"hashed_password": hashed_password})
        await db.commit()

        if identifier_type == "phone" and valid_phone_obj:
            await self.delete_verified_phone_code(valid_phone_obj, "reset")
        elif identifier_type == "email":
            await self.delete_verified_email_code(EmailStr(identifier_value), "reset") 
            
        return {"status": "OK, password changed"}

    async def set_password_for_authenticated_user(self, request: Request, response: Response, data: SetPasswordInput, db: DBDep):
        payload = await self.get_current_user_payload(request, response, db) 
        user_id = payload.id
        
        try:
            user = await db.users.get_one(id=user_id)
        except UserNotFoundException:
            raise UserNotFoundAuthServiceException(detail="Пользователь не найден для смены пароля.")

        if not self.verify_password(data.current_password, user.hashed_password):
            raise IncorrectPasswordServiceException()
        
        self.validate_password_strength(data.new_password)
        hashed_new_password = self.hash_password(data.new_password)
        
        await db.users.edit(id=user_id, data={"hashed_password": hashed_new_password})
        await db.commit()
        return {"status": "Ok", "message": "Пароль успешно обновлен."}

    def validate_password_strength(self, password: str):
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
        )
        errors = policy.test(password)
        if errors:
            raise AuthPasswordTooWeakServiceException

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    async def get_current_user_payload(self, request: Request, response: Response) -> dict:
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not access_token:
            raise AuthTokenMissingServiceException(token_type="Access")
        try:
            return self.decode_access_token(access_token)
        except AuthTokenExpiredServiceException:
            if not refresh_token:
                raise AuthTokenMissingServiceException(token_type="Refresh")
            try:
                payload = self.decode_refresh_token(refresh_token)
                return payload
            except AuthTokenExpiredServiceException:
                raise AuthTokenExpiredServiceException(token_type="Refresh")
            except AuthTokenInvalidServiceException:
                raise AuthTokenInvalidServiceException(token_type="Refresh")
        except AuthTokenInvalidServiceException:
            raise AuthTokenInvalidServiceException(token_type="Access")
        except Exception as e:
            raise MadRussianServiceException(detail=f"Ошибка при обработке токена: {e}")

    def create_tokens(self, payload: dict):
        access_token_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = jwt.encode(
            {**payload, "exp": access_token_exp},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {**payload, "exp": refresh_token_exp},
            settings.JWT_REFRESH_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return access_token, refresh_token

    def create_access_token(self, payload: dict):
        access_token_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(
            {**payload, "exp": access_token_exp},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def decode_access_token(self, token: str):
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise AuthTokenExpiredServiceException(token_type="Access")
        except DecodeError:
            raise AuthTokenInvalidServiceException(token_type="Access")
        except Exception as e:
            raise AuthTokenInvalidServiceException(token_type="Access")

    def decode_refresh_token(self, token: str):
        try:
            return jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise AuthTokenExpiredServiceException(token_type="Refresh")
        except DecodeError:
            raise AuthTokenInvalidServiceException(token_type="Refresh")
        except Exception as e:
            raise AuthTokenInvalidServiceException(token_type="Refresh")
