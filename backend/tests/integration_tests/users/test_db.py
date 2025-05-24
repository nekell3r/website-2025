from pydantic_extra_types.phone_numbers import PhoneNumber

from src.database import get_async_session_maker_null_pool
from src.schemas.users import UserAdd
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


