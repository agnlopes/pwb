"""
HTTP metrics module.

This module provides metrics for tracking HTTP requests:
- Request counts and status codes
- Request/response sizes
- Request durations
- In-progress requests
"""

from prometheus_client import Counter, Histogram, Gauge
from fastapi import Response, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.config import settings
from app.metrics.config import get_metric_name

# Common labels for all metrics
COMMON_LABELS = {
    "environment": settings.ENV,
    "api_version": settings.API_VERSION,
    "component": "api",
    "version": settings.VERSION,
}

# HTTP metrics
http_requests_total = Counter(
    get_metric_name("http_requests_total"),
    "Total number of HTTP requests",
    ["method", "path", "status"] + list(COMMON_LABELS.keys()),
)

http_request_duration_seconds = Histogram(
    get_metric_name("http_request_duration_seconds"),
    "HTTP request duration in seconds",
    ["method", "path"] + list(COMMON_LABELS.keys()),
)

http_requests_inprogress = Gauge(
    get_metric_name("http_requests_inprogress"),
    "Number of HTTP requests in progress",
    ["method", "path"] + list(COMMON_LABELS.keys()),
)

http_request_size_bytes = Histogram(
    get_metric_name("http_request_size_bytes"),
    "HTTP request size in bytes",
    ["method", "path"] + list(COMMON_LABELS.keys()),
)

http_response_size_bytes = Histogram(
    get_metric_name("http_response_size_bytes"),
    "HTTP response size in bytes",
    ["method", "path", "status"] + list(COMMON_LABELS.keys()),
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip metrics if disabled
        if not settings.METRICS_ENABLED:
            return await call_next(request)

        start_time = time.time()

        # Get path components
        path = request.url.path
        components = path.split("/")
        component = components[1] if len(components) > 1 else "root"

        # Prepare labels
        labels = {
            "method": request.method,
            "path": path,
            "environment": settings.ENV,
            "api_version": settings.API_VERSION,
            "component": component,
            "version": settings.VERSION,
        }

        # Track in-progress request
        http_requests_inprogress.labels(**labels).inc()

        try:
            # Get request size
            content_length = request.headers.get("content-length")
            if content_length:
                http_request_size_bytes.labels(**labels).observe(int(content_length))

            response = await call_next(request)
            status = str(response.status_code)

            # Update request count
            http_requests_total.labels(**labels, status=status).inc()

            # Update request duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(**labels).observe(duration)

            # Get response size
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Create new response with the same body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

            # Track response size
            http_response_size_bytes.labels(**labels, status=status).observe(
                len(response_body)
            )

            return response
        except Exception as e:
            # Track failed requests
            http_requests_total.labels(**labels, status="500").inc()
            http_request_duration_seconds.labels(**labels).observe(
                time.time() - start_time
            )
            raise
        finally:
            # Decrease in-progress counter
            http_requests_inprogress.labels(**labels).dec()
