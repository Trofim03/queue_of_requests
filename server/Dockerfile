FROM python:3.12-slim

WORKDIR /app

# Копируем только requirements, чтобы использовать кэш Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Команда по умолчанию (будет переопределена для воркера)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]