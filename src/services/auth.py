from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from jwt import ExpiredSignatureError, DecodeError, InvalidTokenError
from passlib.context import CryptContext
import jwt
from src.config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_tokens(self, payload: dict):
        access_token = jwt.encode(
            {**payload, "exp": datetime.utcnow() + timedelta(minutes=15)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {**payload, "exp": datetime.utcnow() + timedelta(days=7)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return access_token, refresh_token

    def create_access_token(self, payload: dict):
        return jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def decode_token(self, token: str):
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный access токен")
