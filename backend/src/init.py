from yookassa import Configuration

from src.connectors.redis_connector import RedisManager
from src.config import settings

redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)


def init_yookassa(shop_id: str, secret_key: str):
    Configuration.account_id = shop_id
    Configuration.secret_key = secret_key
