FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    CATCHHOT_MYSQL_HOST=localhost \
    CATCHHOT_MYSQL_PORT=3306 \
    CATCHHOT_MYSQL_USER=root \
    CATCHHOT_MYSQL_PASSWORD=3121 \
    CATCHHOT_MYSQL_DATABASE=catchhot \
    CATCHHOT_CORS_ORIGINS=*

WORKDIR /app

RUN sed -i 's|deb.debian.org|mirrors.ustc.edu.cn|g; s|security.debian.org|mirrors.ustc.edu.cn|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY backend ./backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
