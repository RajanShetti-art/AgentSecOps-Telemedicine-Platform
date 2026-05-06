"""Repository-level ASGI entrypoint.

This file makes `python -m uvicorn main:app` work from the repository root by
loading a chosen service's `app.main:app` object. Set the `SERVICE` env var to
`auth`, `patient`, or `appointment` to select a service (defaults to `auth`).

It will also load the selected service's `.env.example` values into
`os.environ` for local development if those variables are not already set,
so import-time DB configuration can succeed.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import sys
from typing import Optional


def _load_env_example(dirpath: Path) -> None:
    env_file = dirpath / ".env.example"
    if not env_file.exists():
        return
    try:
        for raw in env_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            # only set if not already present
            os.environ.setdefault(key, val)
    except Exception:
        # non-fatal for startup; let the real import raise useful errors
        pass


def load_service_app(service: Optional[str] = None):
    service = (service or os.getenv("SERVICE") or "auth").strip()
    # Map canonical names to folder names
    svc_map = {
        "auth": "auth-service",
        "patient": "patient-service",
        "appointment": "appointment-service",
    }
    folder = svc_map.get(service, f"{service}-service")
    service_dir = Path.cwd() / folder
    if not service_dir.exists():
        raise RuntimeError(f"Service folder not found: {service_dir}")

    # Load .env.example values for local defaults
    _load_env_example(service_dir)

    # Ensure Python can import the package named `app` from the service
    sys.path.insert(0, str(service_dir))

    # Import the service's FastAPI app object
    module = importlib.import_module("app.main")
    if not hasattr(module, "app"):
        raise RuntimeError(f"Service module {module.__name__} does not expose `app`")
    return getattr(module, "app")


# Expose `app` at module level for uvicorn: `python -m uvicorn main:app`.
app = load_service_app()
