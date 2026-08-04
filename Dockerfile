FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CATCHHOT_MYSQL_HOST=10.25.101.149 \
    CATCHHOT_MYSQL_PORT=3306 \
    CATCHHOT_MYSQL_USER=root \
    CATCHHOT_MYSQL_PASSWORD=C7C4763g \
    CATCHHOT_MYSQL_DATABASE=catchhot \
    CATCHHOT_CORS_ORIGINS=*

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend ./backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
