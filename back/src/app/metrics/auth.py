"""
Authentication metrics module.

This module provides metrics for tracking authentication and authorization:
- Login attempts and their outcomes
- Authentication failures with specific reasons
- Token operations (create, validate, revoke)
- Token refresh attempts
"""

from prometheus_client import Counter
from app.config import settings
from app.metrics.config import get_metric_name

# Common labels for all metrics
COMMON_LABELS = {
    "environment": settings.ENV,
    "api_version": settings.API_VERSION,
    "component": "api",
    "version": settings.VERSION,
}

# Authentication metrics
auth_attempts_total = Counter(
    get_metric_name("auth_attempts_total"),
    "Total number of authentication attempts",
    ["method", "status"] + list(COMMON_LABELS.keys()),
)

auth_failures_total = Counter(
    get_metric_name("auth_failures_total"),
    "Total number of authentication failures",
    ["reason"] + list(COMMON_LABELS.keys()),
)

token_operations_total = Counter(
    get_metric_name("token_operations_total"),
    "Total number of token operations",
    ["operation", "status"] + list(COMMON_LABELS.keys()),
)

token_refresh_attempts_total = Counter(
    get_metric_name("token_refresh_attempts_total"),
    "Total number of token refresh attempts",
    ["status"] + list(COMMON_LABELS.keys()),
)


def track_auth_attempt(method: str, status: str):
    """Track authentication attempts."""
    labels = {"method": method, "status": status, **COMMON_LABELS}
    auth_attempts_total.labels(**labels).inc()


def track_auth_failure(reason: str):
    """Track authentication failures."""
    labels = {"reason": reason, **COMMON_LABELS}
    auth_failures_total.labels(**labels).inc()


def track_token_operation(operation: str, status: str):
    """Track token operations (create, validate, revoke)."""
    labels = {"operation": operation, "status": status, **COMMON_LABELS}
    token_operations_total.labels(**labels).inc()


def track_token_refresh(status: str):
    """Track token refresh attempts."""
    labels = {"status": status, **COMMON_LABELS}
    token_refresh_attempts_total.labels(**labels).inc()
