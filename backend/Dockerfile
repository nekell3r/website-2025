FROM python:3.13

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Установка рабочей директории
WORKDIR /app

# Сначала копируем только файлы конфигурации Poetry
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копируем всё остальное
COPY . .

# Команда запуска
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]
