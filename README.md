# Telemedicine Microservices Backend

Production-ready FastAPI microservices scaffold for telemedicine workflows.

## Services

- `auth-service` (port `8000`): register and login users with JWT.
- `patient-service` (port `8001`): list and fetch patient records.
- `appointment-service` (port `8002`): book and list appointments.

Each service includes:

- Modular folder layout: `app`, `routes`, `models`, `schemas`
- `Dockerfile`
- `requirements.txt`
- Input validation using Pydantic
- SQLAlchemy ORM with PostgreSQL
- Alembic database migrations
- Basic logging
- `/health` endpoint

Security notes:

- Production secrets should be managed with External Secrets, Sealed Secrets, or a vault.
- Kubernetes hardening manifests are included in `k8s/network-policy.yaml` and `k8s/resource-quota.yaml`.
- Images should be rebuilt and pushed to a registry before deploying to Kubernetes.
- Services run as non-root containers and use read-only root filesystems in Kubernetes.
- The CI pipeline runs secret scanning, SAST, filesystem and image vulnerability scans, IaC checks, SBOM generation, and remediation reporting.

## Environment Setup

Recommended Python version for local development:

- Python 3.11 or 3.12
- Avoid alpha/beta releases such as Python 3.15, which can break database driver installs like `psycopg2-binary`

Create and verify a virtual environment on Windows PowerShell:

```powershell
# from the repo root
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r auth-service\requirements.txt
python -m pip install -r patient-service\requirements.txt
python -m pip install -r appointment-service\requirements.txt
python -c "import uvicorn, fastapi; print('uvicorn', uvicorn.__version__, 'fastapi', fastapi.__version__)"
python -c "import psycopg2; print('psycopg2 OK')"
```

1. Copy `.env.example` to `.env`.
2. Set a strong `JWT_SECRET`.
3. Set strong database passwords in `.env`.

Example:

```env
JWT_SECRET=super-strong-secret-value
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
AUTH_DB_NAME=auth_db
AUTH_DB_USER=auth_user
AUTH_DB_PASSWORD=your-auth-db-password
PATIENT_DB_NAME=patient_db
PATIENT_DB_USER=patient_user
PATIENT_DB_PASSWORD=your-patient-db-password
APPOINTMENT_DB_NAME=appointment_db
APPOINTMENT_DB_USER=appointment_user
APPOINTMENT_DB_PASSWORD=your-appointment-db-password
```

## Run with Docker Compose

```bash
docker compose up --build
```

Each service runs `alembic upgrade head` on startup, so required tables are created automatically.

## Run on Kubernetes

Apply the manifests in this order:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/auth-db.yaml
kubectl apply -f k8s/patient-db.yaml
kubectl apply -f k8s/appointment-db.yaml
kubectl apply -f k8s/auth-service.yaml
kubectl apply -f k8s/patient-service.yaml
kubectl apply -f k8s/appointment-service.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/resource-quota.yaml
```

The database Services must exist before the app Deployments start, and DNS access must remain allowed for the backend pods.

## CI / Security Pipeline

The GitHub Actions workflow now covers:

- Gitleaks secret scanning
- Semgrep SAST
- Trivy filesystem and image scanning
- Kubescape and Checkov IaC checks
- Kyverno policy testing
- Falco YAML/runtime validation workflow
- SBOM generation and signing
- Frontend `npm audit`
- devsecops-agent analysis and remediation tracking

For a quick local check before pushing, run:

```bash
git diff --check
```

## Endpoints

### Auth Service

- `POST /auth/register`
- `POST /auth/login`
- `GET /health`

### Patient Service

- `GET /patients` (Bearer token required)
- `GET /patients/{patient_id}` (Bearer token required)
- `GET /health`

### Appointment Service

- `POST /appointments` (Bearer token required)
- `GET /appointments` (Bearer token required)
- `GET /health`

## Prometheus Metrics Check

To verify Prometheus metrics locally, run a FastAPI service on port `5137` and then inspect the `/metrics` endpoint.

1. Start the service on port `5137`:

```bash
cd auth-service
uvicorn app.main:app --host 0.0.0.0 --port 5137 --reload
```

2. Open the metrics endpoint:

```bash
curl http://localhost:5137/metrics
```

3. The output should be Prometheus text format and include metric families such as:

```text
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/health",method="GET",status_code="200"} 1.0

# HELP http_request_duration_seconds_total Total time spent processing HTTP requests
# TYPE http_request_duration_seconds_total counter
http_request_duration_seconds_total{endpoint="/health",method="GET"} 0.002
```

## Prometheus Troubleshooting

- Target shows `DOWN`:
  - Confirm the FastAPI service is running and listening on the expected port.
  - Verify `monitoring/prometheus.yml` points to the same host and port as the app.
  - Check that Prometheus can reach the service from its network namespace or container.

- `/metrics` endpoint not working:
  - Make sure the service includes `setup_metrics(app)` in `app.main`.
  - Confirm the route exists at `http://localhost:5137/metrics` when the app starts on port `5137`.
  - Review the app logs for startup errors or middleware exceptions.

- Wrong port configuration:
  - Use `5137` in both the FastAPI launch command and the Prometheus target.
  - If you change the app port, update `monitoring/prometheus.yml` to match.
  - Restart Prometheus after changing the scrape config.

- Service not reachable:
  - Check that the service is bound to `0.0.0.0`, not just `127.0.0.1`.
  - If running in Docker, confirm the container port is published to the host.
  - Test the service directly with `curl http://localhost:5137/health` before checking Prometheus.

## Quick Test Flow

## Monitoring Stack

The observability infrastructure includes Prometheus for metrics collection and Grafana for visualization.

### Access Points

- **Prometheus**: [http://localhost:9090](http://localhost:9090)
  - View scrape targets and job status: Status → Targets
  - Query metrics directly: Graph tab
  - Verify all three services are UP: auth-service, patient-service, appointment-service

- **Grafana**: [http://localhost:3000](http://localhost:3000)
  - Default login: `admin` / `admin`
  - Datasource: Prometheus (auto-provisioned)
  - Dashboard: FastAPI Monitoring (auto-provisioned with service metrics)

### Collected Metrics

All FastAPI services expose the following metrics at `/metrics`:

- `http_requests_total`: Counter of total HTTP requests by endpoint, method, and status code
- `http_request_duration_seconds`: Histogram of HTTP request latency
- Standard Prometheus client library metrics (process, Python runtime)

### Dashboard Features

The auto-provisioned Grafana dashboard displays:

- HTTP request rate (requests per second) by service
- Request latency percentiles (p50, p95, p99)
- Error rate by status code
- Service uptime and health checks

### Monitoring Workflow

1. Start all services: `docker compose up -d`
2. Verify services are healthy: `docker ps` (all services should show healthy status)
3. Open Prometheus and confirm targets are UP at [http://localhost:9090/targets](http://localhost:9090/targets)
4. Query example: `rate(http_requests_total[5m])` (request rate over 5 minutes)
5. View live dashboard at [http://localhost:3000](http://localhost:3000) → FastAPI Monitoring

### Metric Export & Alerting

To add Alertmanager, AlertRules, or custom dashboards:

- Edit `monitoring/prometheus.yml` to add alerting rules under `rule_files:`
- Create dashboard JSON in `monitoring/grafana/dashboards/`
- Restart monitoring stack: `docker compose down && docker compose up -d`

## Quick Test Flow

1. Register user:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@example.com","password":"<STRONG_PASSWORD>"}'
```

2. Login and get token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@example.com","password":"<STRONG_PASSWORD>"}'
```

3. Use token against patient and appointment services:

```bash
curl http://localhost:8001/patients -H "Authorization: Bearer <TOKEN>"
```

```bash
curl -X POST http://localhost:8002/appointments \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"doctor_name":"Dr. Smith","appointment_time":"2026-04-15T10:00:00Z","reason":"Routine follow-up"}'
```

## Known Risks

- PostgreSQL uses ephemeral storage in the current manifests, so data is not durable across pod recreation.
- The Falco runtime workflow requires a self-hosted runner and kubeconfig access.
- The CI workflow fetches some tools at runtime, so upstream availability can affect pipeline execution.

## Audit & Verification

Recent checks on the codebase and local runtime showed the following:

- FastAPI apps are defined in `auth-service/app/main.py`, `patient-service/app/main.py`, and `appointment-service/app/main.py`.
- The repo-level `main.py` allows `python -m uvicorn main:app` from the repository root by loading the selected service app.
- Prometheus is scraping all three FastAPI services through `monitoring/prometheus.yml`.
- Grafana is running with datasource and dashboard provisioning enabled.
- Local development is most reliable on Python 3.11 or 3.12.

If you run into import-time database errors, verify that the virtual environment is activated and that the selected service has a valid `DATABASE_URL` in its environment.
