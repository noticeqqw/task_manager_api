FROM python:3.11-slim

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем системные пакеты
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean

# Копируем зависимости Poetry
COPY pyproject.toml .
COPY poetry.lock .

# Копируем .env файл
COPY .env .

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости проекта
RUN poetry install --no-root

# Копируем весь проект
COPY . .

# Команда запуска FastAPI
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
