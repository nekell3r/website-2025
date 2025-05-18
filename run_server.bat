@echo off
echo Запуск FastAPI через poetry...
start cmd /k "poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 5 >nul

echo Запуск ngrok...
start cmd /k "ngrok http 8000"