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

# Copy startup script and make it executable
COPY prestart.sh .

# Папка для сертификатов (реальные ключи прокидываются через volume)
RUN mkdir -p /app/certs

EXPOSE 8000

RUN chmod +x prestart.sh

ENTRYPOINT ["./prestart.sh"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]