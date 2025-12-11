FROM python:3.12-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# API
FROM base as api
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Consumer
FROM base as consumer
CMD ["python", "-m", "src.consumer.main"]

