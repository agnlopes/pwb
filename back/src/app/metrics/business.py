"""
Business metrics module.

This module provides metrics for tracking business operations:
- Active users count
- User actions (create, read, update, delete, etc.)
"""

from prometheus_client import Counter, Gauge
from app.config import settings
from app.metrics.config import get_metric_name

# Common labels for all metrics
COMMON_LABELS = {
    "environment": settings.ENV,
    "api_version": settings.API_VERSION,
    "component": "api",
    "version": settings.VERSION,
}

# Business metrics
active_users = Gauge(
    get_metric_name("active_users"),
    "Number of active users",
    list(COMMON_LABELS.keys()),
)

user_actions_total = Counter(
    get_metric_name("user_actions_total"),
    "Total number of user actions",
    ["action", "target_type"] + list(COMMON_LABELS.keys()),
)


def track_user_action(action: str, target_type: str):
    """Track user actions."""
    labels = {"action": action, "target_type": target_type, **COMMON_LABELS}
    user_actions_total.labels(**labels).inc()


def update_active_users(count: int):
    """Update the number of active users."""
    active_users.labels(**COMMON_LABELS).set(count)
