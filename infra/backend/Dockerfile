FROM python:3.11

WORKDIR /

COPY ./requirements-admin.txt .

RUN pip install --no-cache-dir -r requirements-admin.txt

COPY src/app src/app
COPY src/alembic src/alembic
COPY src/alembic.ini src/alembic.ini
COPY templates templates
COPY infra/data infra/data
CMD ["/bin/sh", "-c", "alembic -c src/alembic.ini upgrade head && uvicorn src.app.main:app --forwarded-allow-ips '*' --proxy-headers --host 0.0.0.0 --port 8000"]
