# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==1.7.1

# Настраиваем Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы Poetry для установки зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# Копируем исходный код
COPY src/ ./src/
COPY setup.cfg ./

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Создаем пользователя для запуска приложения (безопасность)
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт (если потребуется webhook)
EXPOSE 8000

# Команда запуска
CMD ["python", "src/main.py"]
