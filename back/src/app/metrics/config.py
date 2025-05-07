"""
Metrics configuration module.

This module provides configuration for Prometheus metrics:
- Metrics endpoint setup
- Default metrics configuration
- Custom metrics registry
"""

from prometheus_client import (
    make_asgi_app,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    generate_latest,
    REGISTRY,
)
from fastapi import FastAPI, Request, Response
from app.config import settings


def get_metric_name(name: str) -> str:
    """
    Get the metric name with optional prefix.

    Args:
        name: Base metric name

    Returns:
        Metric name with prefix if configured
    """
    if not settings.METRICS_PREFIX:
        return name

    # Remove prometheus_ prefix if it exists
    if name.startswith("prometheus_"):
        name = name[11:]  # len("prometheus_") = 11

    return f"{settings.METRICS_PREFIX}_{name}"


def configure_metrics(app: FastAPI) -> None:
    """
    Configure metrics for the application.

    This function:
    1. Creates a custom registry if metrics are disabled
    2. Sets up the metrics endpoint
    3. Configures default metrics
    4. Adds middleware for request tracking

    Args:
        app: FastAPI application instance
    """

    # Add metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics(request: Request) -> Response:
        """Metrics endpoint for Prometheus."""
        if not settings.METRICS_ENABLED:
            return Response(
                content="Metrics are disabled", status_code=404, media_type="text/plain"
            )

        # Generate metrics content using the default registry
        content = generate_latest(REGISTRY)

        # Add prefix to all metric names if configured
        if settings.METRICS_PREFIX:
            content_str = content.decode()
            prefixed_content = "\n".join(
                f"{settings.METRICS_PREFIX}_{line}"
                if line and not line.startswith("#")
                else line
                for line in content_str.split("\n")
            )
            content = prefixed_content.encode()

        return Response(
            content=content, status_code=200, media_type=CONTENT_TYPE_LATEST
        )
