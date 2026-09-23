FROM python:3.14-slim

ENV APP_ENV=production \
    DB_BACKEND=sqlite \
    API_DOCS_ENABLED=false \
    DB_NAME=/data/products.db \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY api.py api_errors.py config.py database.py product_service.py ./
COPY persistence.py repositories.py migrations.py ./
COPY schemas ./schemas

RUN mkdir /data && chown -R app:app /app /data

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port = os.getenv('PORT') or '8000'; urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3).close()"]

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
