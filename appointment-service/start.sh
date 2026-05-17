#!/bin/sh
set -e

export PYTHONPATH=/service

# Wait for Postgres to accept connections before migrating.
python - <<'PY'
import os
import socket
import sys
import time

host = os.getenv("DB_HOST", "db")
for _ in range(60):
	try:
		with socket.create_connection((host, 5432), timeout=2):
			sys.exit(0)
	except OSError:
		time.sleep(2)

raise SystemExit("Postgres did not become ready in time")
PY

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8002
