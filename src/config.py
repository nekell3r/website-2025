from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # нельзя логировать этот адрес - внутри пароль лежит

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DAYS: int

    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_API_URL: str

    SMSRU_API_ID: int

    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).parent.parent / '.local_env_example'}"
        # env_file=f"{Path(__file__).parent.parent / '.env_example'}"
        # env_file=f"{Path(__file__).parent.parent / '.env'}"
    )


settings = Settings()

