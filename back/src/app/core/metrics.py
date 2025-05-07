from typing import Optional

from prometheus_client import Counter, Gauge, Histogram


class Metrics:
    """
    Centralized metrics registry for the application.

    This class organizes metrics by feature/module, providing a structured way to track
    application performance, usage patterns, and system health. Each feature has its own
    nested class containing related metrics.

    Usage:
        from app.core.metrics import metrics

        # Increment a counter
        metrics.Database.SESSION_CREATED.inc()

        # Set a gauge value
        metrics.Database.ACTIVE_SESSIONS.set(5)

        # Record a duration
        metrics.Database.SESSION_DURATION.observe(1.5)

        # Use labels
        metrics.Database.POOL_CONNECTIONS.labels(state='idle').set(3)

    Metric Types:
        - Counter: Monotonically increasing counter (e.g., total requests)
        - Gauge: Current value that can go up or down (e.g., active sessions)
        - Histogram: Samples observations and counts them in configurable buckets
    """

    class Database:
        """
        Database related metrics.

        Tracks session management, transaction handling, and connection pool usage.
        These metrics help monitor database health and performance.

        Metrics:
            Session Management:
                - ACTIVE_SESSIONS: Current number of active database sessions
                - SESSION_CREATED: Total sessions created since startup
                - SESSION_CLOSED: Total sessions closed since startup
                - SESSION_DURATION: Distribution of session durations

            Transaction Handling:
                - TRANSACTION_COMMITS: Successful transaction commits
                - TRANSACTION_ROLLBACKS: Failed transactions requiring rollback

            Connection Pool:
                - POOL_CONNECTIONS: Current state of connection pool (idle/in_use)

            Performance:
                - QUERY_DURATION: Distribution of query execution times

        Example Prometheus Queries:
            # Active sessions over time
            db_active_sessions

            # Session creation rate (per minute)
            rate(db_session_created_total[1m])

            # Average session duration
            rate(db_session_duration_seconds_sum[5m]) / rate(db_session_duration_seconds_count[5m])

            # Transaction success rate
            rate(db_transaction_commits_total[5m]) / (rate(db_transaction_commits_total[5m]) + rate(db_transaction_rollbacks_total[5m]))

            # Connection pool utilization
            db_pool_connections{state="in_use"} / (db_pool_connections{state="idle"} + db_pool_connections{state="in_use"})
        """

        # Session metrics
        ACTIVE_SESSIONS = Gauge(
            "db_active_sessions", "Number of active database sessions"
        )

        SESSION_CREATED = Counter(
            "db_session_created_total", "Total number of database sessions created"
        )

        SESSION_CLOSED = Counter(
            "db_session_closed_total", "Total number of database sessions closed"
        )

        # Transaction metrics
        TRANSACTION_COMMITS = Counter(
            "db_transaction_commits_total",
            "Total number of successful transaction commits",
        )

        TRANSACTION_ROLLBACKS = Counter(
            "db_transaction_rollbacks_total", "Total number of transaction rollbacks"
        )

        # Connection pool metrics
        POOL_CONNECTIONS = Gauge(
            "db_pool_connections",
            "Number of connections in the pool",
            ["state"],  # 'idle' or 'in_use'
        )

        # Performance metrics
        SESSION_DURATION = Histogram(
            "db_session_duration_seconds",
            "Duration of database sessions in seconds",
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
        )

        QUERY_DURATION = Histogram(
            "db_query_duration_seconds",
            "Duration of database queries in seconds",
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
        )

    class Auth:
        """Authentication related metrics"""

        LOGIN_ATTEMPTS = Counter(
            "auth_login_attempts_total",
            "Total number of login attempts",
            ["status"],  # 'success' or 'failure'
        )

        TOKEN_REFRESHES = Counter(
            "auth_token_refreshes_total", "Total number of token refreshes"
        )

    class Portfolio:
        """Portfolio related metrics"""

        PORTFOLIO_CREATED = Counter(
            "portfolio_created_total", "Total number of portfolios created"
        )

        PORTFOLIO_UPDATED = Counter(
            "portfolio_updated_total", "Total number of portfolio updates"
        )

        PORTFOLIO_DELETED = Counter(
            "portfolio_deleted_total", "Total number of portfolios deleted"
        )

    class Asset:
        """Asset related metrics"""

        ASSET_CREATED = Counter("asset_created_total", "Total number of assets created")

        ASSET_UPDATED = Counter("asset_updated_total", "Total number of asset updates")

        ASSET_DELETED = Counter("asset_deleted_total", "Total number of assets deleted")


# Global metrics instance
metrics = Metrics()
