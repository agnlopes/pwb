"""
Database metrics module.

This module provides metrics for tracking database operations:
- Operation counts and durations
- Connection pool statistics
"""

from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.config import settings
from app.metrics.config import get_metric_name

# Common labels for all metrics
COMMON_LABELS = {
    "environment": settings.ENV,
    "api_version": settings.API_VERSION,
    "component": "api",
    "version": settings.VERSION,
}

# Database operation metrics
database_operations_total = Counter(
    get_metric_name("database_operations_total"),
    "Total number of database operations",
    ["operation", "table", "db_type"] + list(COMMON_LABELS.keys()),
)

database_operation_duration_seconds = Histogram(
    get_metric_name("database_operation_duration_seconds"),
    "Database operation duration in seconds",
    ["operation", "table", "db_type"] + list(COMMON_LABELS.keys()),
)

# Database pool metrics
db_pool_size = Gauge(
    get_metric_name("db_pool_size"),
    "Number of connections in the pool",
    ["db_type"] + list(COMMON_LABELS.keys()),
)

db_pool_checkedin = Gauge(
    get_metric_name("db_pool_checkedin"),
    "Number of connections checked in to the pool",
    ["db_type"] + list(COMMON_LABELS.keys()),
)

db_pool_checkedout = Gauge(
    get_metric_name("db_pool_checkedout"),
    "Number of connections checked out from the pool",
    ["db_type"] + list(COMMON_LABELS.keys()),
)

db_pool_overflow = Gauge(
    get_metric_name("db_pool_overflow"),
    "Number of connections in overflow",
    ["db_type"] + list(COMMON_LABELS.keys()),
)


def track_database_operation(operation: str, table: str, duration: float):
    """Track database operations."""
    labels = {
        "operation": operation,
        "table": table,
        "db_type": settings.DB_TYPE,
        **COMMON_LABELS,
    }
    database_operations_total.labels(**labels).inc()
    database_operation_duration_seconds.labels(**labels).observe(duration)


def configure_db_metrics(engine: Engine):
    """Configure database pool metrics using SQLAlchemy event listeners."""

    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Track when a connection is checked out from the pool."""
        labels = {"db_type": settings.DB_TYPE, **COMMON_LABELS}
        db_pool_checkedout.labels(**labels).inc()
        db_pool_checkedin.labels(**labels).dec()

    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        """Track when a connection is checked in to the pool."""
        labels = {"db_type": settings.DB_TYPE, **COMMON_LABELS}
        db_pool_checkedin.labels(**labels).inc()
        db_pool_checkedout.labels(**labels).dec()

    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        """Track when a new connection is created."""
        labels = {"db_type": settings.DB_TYPE, **COMMON_LABELS}
        db_pool_size.labels(**labels).inc()

    @event.listens_for(engine, "close")
    def receive_close(dbapi_connection, connection_record):
        """Track when a connection is closed."""
        labels = {"db_type": settings.DB_TYPE, **COMMON_LABELS}
        db_pool_size.labels(**labels).dec()

    @event.listens_for(engine, "overflow")
    def receive_overflow(dbapi_connection, connection_record):
        """Track when the pool overflows."""
        labels = {"db_type": settings.DB_TYPE, **COMMON_LABELS}
        db_pool_overflow.labels(**labels).inc()
