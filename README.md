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
