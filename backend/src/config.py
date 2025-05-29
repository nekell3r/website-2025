from functools import lru_cache
from typing import Literal, Any

# Убираем прямой вызов load_dotenv из python-dotenv.
# Для тестов полагаемся на pytest-dotenv (через pytest.ini).
# Для запуска приложения (LOCAL/DEV/PROD) переменные окружения должны быть установлены
# либо системно, либо через Docker, либо загружены в точке входа приложения (например, main.py),
# но НЕ здесь глобально в config.py, чтобы не мешать pytest.

from pydantic_settings import BaseSettings, SettingsConfigDict

# print(f"DEBUG (config.py @ top): os.environ.get('MODE') = {os.environ.get('MODE')}")


class _SettingsStore:
    _instance: BaseSettings | None = None  # Будет хранить экземпляр ActualSettings

    @staticmethod
    @lru_cache(maxsize=1)  # Кэшируем, чтобы инициализация была только раз
    def get_instance() -> BaseSettings:
        if _SettingsStore._instance is None:
            # print(f"DEBUG (config.py - _SettingsStore.get_instance): Lazily initializing ActualSettings. Current os.environ.get('MODE') = {os.environ.get('MODE')}")

            class ActualSettings(BaseSettings):
                MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]
                DB_NAME: str
                DB_USER: str
                DB_PASS: str
                DB_HOST: str
                DB_PORT: int

                REDIS_HOST: str = "localhost"
                REDIS_PORT: int = 6379
                JWT_SECRET_KEY: str = "default_jwt_secret"
                JWT_ALGORITHM: str = "HS256"
                ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
                JWT_REFRESH_SECRET_KEY: str = "default_jwt_refresh_secret"
                REFRESH_TOKEN_EXPIRE_DAYS: int = 7
                YOOKASSA_SHOP_ID: str = "default_shop_id"
                YOOKASSA_SECRET_KEY: str = "default_yookassa_secret"
                YOOKASSA_API_URL: str = "https://api.yookassa.ru/v3/payments"
                SMSRU_API_ID: int = 0

                @property
                def DB_URL(self) -> str:
                    return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

                @property
                def REDIS_URL(self) -> str:
                    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

                model_config = SettingsConfigDict(
                    env_file=None,  # Pydantic должен читать только из os.environ
                    extra="ignore",
                )

            _SettingsStore._instance = ActualSettings()
            # print(f"DEBUG (config.py - _SettingsStore.get_instance): ActualSettings initialized. MODE={_SettingsStore._instance.MODE}, DB_HOST={_SettingsStore._instance.DB_HOST}")
        return _SettingsStore._instance


# Создаем прокси-объект, который будет использоваться как `settings`
class SettingsProxy:
    def __getattr__(self, name: str) -> Any:
        # Это вызовет _SettingsStore.get_instance() только при первом обращении к любому атрибуту settings
        instance = _SettingsStore.get_instance()
        if instance is None:  # Добавим проверку на всякий случай
            raise AttributeError(
                f"Settings instance is None, cannot get attribute '{name}'"
            )
        return getattr(instance, name)


settings = SettingsProxy()

# print(f"DEBUG (config.py @ bottom): `settings` object is now a SettingsProxy. Actual initialization is deferred until first attribute access.")

# Далее будет SettingsProxy и settings = SettingsProxy()
# ... (остальная часть файла будет в следующем шаге)
