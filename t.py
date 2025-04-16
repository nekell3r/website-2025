from sqlalchemy import create_engine, inspect
from src.config import settings


def list_tables_sync():
    engine = create_engine(settings.DB_URL.replace("+asyncpg", ""))
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("📦 Таблицы в БД:", tables)


list_tables_sync()
