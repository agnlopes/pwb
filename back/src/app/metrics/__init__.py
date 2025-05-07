"""
Metrics package for the application.

This package provides Prometheus metrics for monitoring various aspects of the application:
- Authentication and authorization
- Business operations
- Database operations
- HTTP requests
- System metrics
"""

from app.config import settings

# Common labels for all metrics
COMMON_LABELS = {
    "environment": settings.ENV,
    "api_version": settings.API_VERSION,
    "component": "api",
    "version": settings.VERSION,
}

from app.metrics.auth import (
    auth_attempts_total,
    auth_failures_total,
    token_operations_total,
    token_refresh_attempts_total,
    track_auth_attempt,
    track_auth_failure,
    track_token_operation,
    track_token_refresh,
)

from app.metrics.business import (
    active_users,
    user_actions_total,
    track_user_action,
    update_active_users,
)

from app.metrics.database import (
    database_operations_total,
    database_operation_duration_seconds,
    db_pool_size,
    db_pool_checkedin,
    db_pool_checkedout,
    db_pool_overflow,
    track_database_operation,
    configure_db_metrics,
)

from app.metrics.http import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_inprogress,
    http_request_size_bytes,
    http_response_size_bytes,
    MetricsMiddleware,
)

from app.metrics.config import configure_metrics

__all__ = [
    # Auth metrics
    "auth_attempts_total",
    "auth_failures_total",
    "token_operations_total",
    "token_refresh_attempts_total",
    "track_auth_attempt",
    "track_auth_failure",
    "track_token_operation",
    "track_token_refresh",
    # Business metrics
    "active_users",
    "user_actions_total",
    "track_user_action",
    "update_active_users",
    # Database metrics
    "database_operations_total",
    "database_operation_duration_seconds",
    "db_pool_size",
    "db_pool_checkedin",
    "db_pool_checkedout",
    "db_pool_overflow",
    "track_database_operation",
    "configure_db_metrics",
    # HTTP metrics
    "http_requests_total",
    "http_request_duration_seconds",
    "http_requests_inprogress",
    "http_request_size_bytes",
    "http_response_size_bytes",
    "MetricsMiddleware",
    # Configuration
    "configure_metrics",
]
