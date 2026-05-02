FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Сначала зависимости — Docker закэширует слой если код изменился, а requirements нет
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Исходный код
COPY src/      ./src/
COPY migrations/  ./migrations/
COPY alembic.ini .

# Папка для сертификатов (реальные ключи прокидываются через volume)
RUN mkdir -p /app/certs

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]