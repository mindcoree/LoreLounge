# ─── Builder stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем только requirements для кэширования слоя зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Добавляем /app/src в PYTHONPATH, чтобы модули находились без пакетного префикса
    PYTHONPATH=/app/src

WORKDIR /app

# Копируем установленные зависимости из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код
COPY src/    ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Сертификаты прокидываются через docker-compose volume (certs/:ro)
# Но на случай локального запуска создаём папку
RUN mkdir -p /app/certs

EXPOSE 8000

# Запуск uvicorn с workers для production
# --workers 1 для dev (можно увеличить через env)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]