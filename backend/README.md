# MadRussian - Backend

Эта ветка представляет собой бэкенд-приложение для веб-сайта MadRussian, разработанное на Python с использованием фреймворка FastAPI. Приложение обеспечивает аутентификацию пользователей, управление курсами/продуктами, систему отзывов, интеграцию с платежной системой ЮKassa и другие функции.

## Основные технологии

*   **Язык программирования**: Python 3.11+
*   **Фреймворк**: FastAPI
*   **База данных**: PostgreSQL (асинхронное взаимодействие через `asyncpg`)
*   **Миграции БД**: Alembic
*   **Кэширование**: Redis (`fastapi-cache`)
*   **Валидация данных**: Pydantic
*   **Управление зависимостями**: Poetry
*   **Аутентификация**: JWT (access и refresh токены в cookies)
*   **Платежная система**: ЮKassa (интеграция для обработки платежей)
*   **Отправка SMS**: Интеграция с SMS.ru (для кодов подтверждения)
*   **Тестирование**: Pytest, `pytest-asyncio`, `pytest-dotenv`

## Функционал

*   Регистрация пользователей (по номеру телефона или email с подтверждением кодом).
*   Аутентификация пользователей (логин/пароль, JWT токены).
*   Обновление токенов (refresh token).
*   Сброс пароля (по номеру телефона или email с подтверждением кодом).
*   Управление информацией о пользователе (личный кабинет).
*   Административная панель для управления пользователями (базовые функции).
*   Управление продуктами/курсами (CRUD операции для администраторов).
*   Система отзывов о продуктах/курсах.
*   Интеграция с платежной системой ЮKassa для создания и обработки платежей.
*   Обработка вебхуков от ЮKassa для обновления статусов платежей.

## Структура проекта

*   `src/`: Основной исходный код приложения.
    *   `api/`: Роутеры FastAPI, определяющие эндпоинты.
    *   `config.py`: Конфигурация приложения (загрузка из переменных окружения).
    *   `database.py`: Настройка подключения к базе данных.
    *   `dependencies/`: Зависимости FastAPI (например, для аутентификации, получения сессии БД).
    *   `exceptions/`: Кастомные классы исключений и их обработчики.
    *   `models/`: ORM-модели SQLAlchemy для таблиц базы данных.
    *   `repositories/`: Классы-репозитории для взаимодействия с базой данных (абстракция над ORM).
    *   `schemas/`: Pydantic-схемы для валидации данных запросов и ответов.
    *   `services/`: Бизнес-логика приложения.
    *   `utils/`: Вспомогательные утилиты.
    *   `main.py`: Точка входа в приложение FastAPI.
    *   `init.py`: Инициализация внешних сервисов (Redis, Yookassa).
*   `migrations/`: Файлы миграций Alembic.
    *   `versions/`: Сгенерированные миграции.
    *   `env.py`: Конфигурация Alembic.
*   `tests/`: Тесты для приложения.
    *   `unit_tests/`: Модульные тесты.
    *   `integration_tests/`: Интеграционные тесты.
*   `alembic.ini`: Конфигурационный файл Alembic.
*   `Dockerfile`: Файл для сборки Docker-образа приложения (находится в `backend/`).
*   `docker-compose.yml`: (Находится в **корне репозитория**, т.е. на уровень выше `backend/`) Файл для оркестрации контейнеров (приложение, БД, Redis).
*   `.env`: (Находится в **корне репозитория** для `docker-compose`) Файл с переменными окружения для Docker.
*   `.local_env_example`: Пример файла с переменными окружения для локальной разработки (внутри `backend/`).
*   `.env-test`: Переменные окружения для тестов (внутри `backend/`).
*   `pyproject.toml` и `poetry.lock`: Файлы управления зависимостями Poetry (внутри `backend/`).
*   `pytest.ini`: Конфигурация Pytest (внутри `backend/`).

## Установка и запуск

### Требования

*   Python 3.12 или выше.
*   Poetry (менеджер зависимостей). Инструкции по установке: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
*   Docker и Docker Compose (для запуска в контейнерах).

### Локальный запуск (внутри директории `backend/`)

1.  **Клонируйте репозиторий (если еще не сделали):**
    ```bash
    git clone <URL_РЕПОЗИТОРИЯ_MadRussian>
    cd MadRussian_NewClone/backend 
    ```
    Если вы уже в `MadRussian_NewClone`, просто перейдите в `cd backend`.

2.  **Установите зависимости:**
    ```bash
    poetry install
    ```
    Эта команда создаст виртуальное окружение (если его нет) и установит все необходимые пакеты.

3.  **Настройте переменные окружения:**
    *   Скопируйте файл `backend/.local_env_example` в новый файл `backend/.local_env_example`.
        ```bash
        cp .local_env_example .local_env_example 
        ```
        ИЛИ, если вы хотите использовать стандартный `backend/.env` для локального запуска, скопируйте `backend/.local_env_example` в `backend/.env` и измените `backend/src/main.py`, чтобы он читал `.env` при `MODE=LOCAL`.
        *   Откройте созданный файл (`backend/.local_env_example` или `backend/.env`) и отредактируйте значения переменных.
    *   Откройте созданный файл (`.local_env_example` или `.env`) и отредактируйте значения переменных:
        *   `MODE=LOCAL`
        *   `DB_USER`, `DB_PASS`, `DB_NAME`, `DB_HOST`, `DB_PORT`: Данные для подключения к вашему локальному PostgreSQL.
        *   `REDIS_HOST`, `REDIS_PORT`: Данные для подключения к вашему локальному Redis.
        *   `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`: Сгенерируйте надежные случайные строки.
        *   `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`: Ваши тестовые или боевые ключи ЮKassa.
        *   `SMSRU_API_ID`: Ваш API ID для SMS.ru.

4.  **Убедитесь, что PostgreSQL и Redis запущены** и доступны по указанным в переменных окружения адресам.

5.  **Примените миграции базы данных:**
    Активируйте виртуальное окружение Poetry, если вы еще не в нем:
    ```bash
    poetry shell
    ```
    Запустите миграции:
    ```bash
    alembic upgrade head
    ```

6.  **Запустите приложение FastAPI:**
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Приложение будет доступно по адресу `http://localhost:8000`.

### Запуск с использованием Docker (рекомендуется)

Этот способ описывает запуск с использованием `docker-compose.yml` и файла `.env`, расположенных в **корне репозитория** (`MadRussian_NewClone/`).

1.  **Убедитесь, что Docker и Docker Compose установлены.**
2.  **Создайте `docker-compose.yml` в корне репозитория** (на одном уровне с папками `backend/` и `frontend/`). Пример `docker-compose.yml`:
    ```yaml
    services:
      web:
        build:
          context: ./backend # Указывает на папку с Dockerfile
          dockerfile: Dockerfile
        env_file:
          - ./.env # Использует .env из корня репозитория
        ports:
          - "7777:8000" # Пример: порт хоста 7777, порт контейнера 8000
        depends_on:
          db:
            condition: service_healthy
          cache:
            condition: service_healthy
        volumes:
          - ./backend:/app # Монтирование кода для разработки (опционально)
        networks:
          - myNetwork

      db:
        image: postgres:15
        env_file:
          - ./.env # Использует POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB из .env
        ports:
          - "5433:5432" # Пример: порт хоста 5433, стандартный порт PG 5432
        volumes:
          - pg-data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
          interval: 10s
          timeout: 5s
          retries: 5
        networks:
          - myNetwork

      cache:
        image: redis:7
        ports:
          - "6380:6379" # Пример: порт хоста 6380, стандартный порт Redis 6379
        healthcheck:
          test: ["CMD", "redis-cli", "ping"]
          interval: 10s
          timeout: 5s
          retries: 5
        networks:
          - myNetwork

    volumes:
      pg-data:

    networks:
      myNetwork:
        driver: bridge
    ```
3.  **Создайте файл `.env` в корне репозитория.** Заполните его переменными окружения. Важно:
    *   `DB_HOST=db` (имя сервиса PostgreSQL из `docker-compose.yml`)
    *   `REDIS_HOST=cache` (имя сервиса Redis из `docker-compose.yml`)
    *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (для сервиса `db`)
    *   Остальные переменные, как в `.local_env_example` (например, `JWT_SECRET_KEY`, `YOOKASSA_SHOP_ID`, etc.).
    *   Установите `MODE=PROD` или `MODE=DEV`.
    Пример корневого `.env`:
    ```env
    MODE=DEV

    # PostgreSQL - для сервиса web (приложения)
    DB_HOST=db
    DB_PORT=5432 # Внутренний порт PostgreSQL в Docker сети
    DB_USER=your_db_user
    DB_PASS=your_db_password
    DB_NAME=your_db_name

    # PostgreSQL - для сервиса db (самого PostgreSQL)
    POSTGRES_USER=your_db_user 
    POSTGRES_PASSWORD=your_db_password
    POSTGRES_DB=your_db_name

    # Redis
    REDIS_HOST=cache
    REDIS_PORT=6379 # Внутренний порт Redis в Docker сети

    # JWT
    JWT_SECRET_KEY=your_super_secret_jwt_key
    JWT_REFRESH_SECRET_KEY=your_super_secret_refresh_jwt_key
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7

    # Yookassa
    YOOKASSA_SHOP_ID=your_shop_id
    YOOKASSA_SECRET_KEY=your_yookassa_secret_key

    # SMS.ru (если используется)
    # SMSRU_API_ID=your_smsru_api_id
    ```

4.  **Соберите и запустите контейнеры (из корня репозитория):**
    ```bash
    docker-compose up --build -d
    ```
5.  **Примените миграции** (если это первый запуск или были изменения схемы):
    Выполните из корня репозитория:
    ```bash
    docker-compose exec web alembic upgrade head
    ```
    Приложение FastAPI (сервис `web`) будет доступно по порту, указанному в `ports` для сервиса `web` в `docker-compose.yml` (например, `http://localhost:7777`).

## Тестирование (внутри директории `backend/`)

Для запуска тестов используйте Pytest. Убедитесь, что у вас настроен файл `backend/.env-test` с конфигурацией для тестовой среды (включая `MODE=TEST` и отдельную тестовую БД, которая должна быть запущена локально или в Docker, но настроена на подключение из `.env-test`).

Перейдите в директорию `backend/`:
```bash
cd backend # если вы в корне репозитория
```
Активируйте виртуальное окружение Poetry:
```bash
poetry env activate
```
Запустите тесты:
```bash
pytest
```
Или с большей детализацией:
```bash
pytest -s -v
```

## API Документация

После запуска приложения FastAPI автоматически генерирует интерактивную API документацию:

*   **Swagger UI**: доступен по адресу `http://localhost:8000/docs` (замените порт, если необходимо).
*   **ReDoc**: доступен по адресу `http://localhost:8000/redoc`.

## Дальнейшие шаги и улучшения (TODO)

*   [ ] Добавить более детальное логирование.
*   [ ] Настроить CI/CD для автоматической сборки, тестирования и развертывания.
*   [ ] Усилить безопасность (например, более строгие политики CORS для продакшена, лимиты запросов).
*   [ ] Расширить административные функции.
*   [ ] Добавить больше интеграционных и e2e тестов.

---

Автор: Жабский Павел
