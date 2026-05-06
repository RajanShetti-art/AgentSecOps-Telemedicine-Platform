"""Prometheus metrics initialization and middleware for FastAPI services."""

from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware


request_counter = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""

    async def dispatch(self, request: Request, call_next):
        """Track request count, status, and latency."""
        if request.url.path == "/metrics":
            return await call_next(request)

        endpoint = request.url.path
        status_code = 500
        start_time = perf_counter()

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = perf_counter() - start_time
            request_counter.labels(
                method=request.method,
                endpoint=endpoint,
                status=str(status_code),
            ).inc()
            request_duration.labels(endpoint=endpoint).observe(duration)


def setup_metrics(app: FastAPI) -> None:
    """Configure Prometheus metrics for a FastAPI application."""
    app.add_middleware(MetricsMiddleware)

    @app.get(
        "/metrics",
        tags=["monitoring"],
        responses={200: {"description": "Prometheus metrics in text format"}},
    )
    async def metrics() -> Response:
        """Expose Prometheus metrics."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
