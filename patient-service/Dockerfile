FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Create non-root user and use it (stable across Debian-based images)
RUN groupadd --gid 10001 appgroup && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin appuser
RUN chown -R appuser:appgroup /service

USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health').read()"

EXPOSE 8001

CMD ["./start.sh"]
