import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from uuid import UUID
from typing import Any, Dict, Literal

from sqlmodel.ext.asyncio.session import AsyncSession  # type: ignore

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.portfolio_ledger import PortfolioLedger
from app.utils.tracing import get_correlation_id


def setup_logging() -> None:
    """Configure logging with both file and stdout handlers."""
    # Create log directory if it doesn't exist
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add file handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_handler.setFormatter(
        JsonFormatter() if settings.LOG_FORMAT == "json" else TextFormatter()
    )
    logger.addHandler(file_handler)

    # Add stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(settings.LOG_STDOUT_LEVEL)
    stdout_handler.setFormatter(
        JsonFormatter() if settings.LOG_FORMAT == "json" else TextFormatter()
    )
    logger.addHandler(stdout_handler)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
            "component": getattr(record, "component", record.name),  # Use record.name as fallback
        }
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "details"):
            log_data["details"] = record.details
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Format log records as plain text."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as plain text."""
        correlation_id = get_correlation_id()
        component = getattr(record, "component", record.name)  # Use record.name as fallback
        message = f"[{correlation_id}] [{component}] {record.getMessage()}"
        if hasattr(record, "user_id"):
            message = f"[user_id={record.user_id}] {message}"
        if hasattr(record, "action"):
            message = f"[action={record.action}] {message}"
        if hasattr(record, "details"):
            message = f"[details={record.details}] {message}"
        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"
        return message


async def log_activity(
    message: dict = {},
    level: str = "info",
    component: str = "system",
):
    """Log an activity with correlation ID."""
    loggers = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    # Check for valid log level
    if level not in loggers:
        raise ValueError(f"Invalid log level: {level}. Choose from list(loggers.keys())")

    # Add correlation ID to message
    correlation_id = get_correlation_id()
    if correlation_id:
        message["correlation_id"] = correlation_id

    # Log the activity
    logger = logging.getLogger()
    extra = {"component": component}
    logger.log(loggers[level], json.dumps(message), extra=extra)


async def log_user_action(
    session: AsyncSession,
    user_id: UUID,
    action: str,
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
    path: str,
    target_type: str | None = None,
    target_id: UUID | None = None,
    details: dict | None = None,
) -> None:
    """
    Log a user action performed through an API endpoint.
    
    Args:
        session: Database session
        user_id: ID of the user performing the action
        action: The action being performed (e.g., "create", "update", "delete", "list")
        method: HTTP method of the request
        path: API path of the request
        target_type: Type of the target resource (e.g., "user", "portfolio")
        target_id: ID of the target resource
        details: Additional details about the action
    """
    # Skip logging if we're only logging write operations and this is a read operation
    if settings.LOG_USER_ACTIONS == "write" and method == "GET":
        return

    # Create audit log entry
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details={
            "method": method,
            "path": path,
            **(details or {}),
        },
        timestamp=datetime.utcnow(),
    )

    # Commit the audit log entry
    session.add(log_entry)
    await session.commit()

    # Create a log message
    log_message = {
        "type": "user_action",
        "user_id": str(user_id),
        "action": action,
        "method": method,
        "path": path,
        "target_type": target_type,
        "target_id": str(target_id) if target_id else None,
        "details": details,
    }

    # Log the user action
    await log_activity(
        message=log_message,
        level="info",
        component="api",
    )


async def record_portfolio_change(
    session: AsyncSession,
    portfolio_id: UUID,
    change_type: str,
    details: dict,
) -> None:
    """Log a portfolio change with correlation ID."""
    ledger_entry = PortfolioLedger(
        portfolio_id=portfolio_id,
        change_type=change_type,
        details=details,
        timestamp=datetime.utcnow(),
    )

    # Commit the ledger entry
    session.add(ledger_entry)
    await session.commit()

    # Create a log message
    log_message = {
        "type": "portfolio_change",
        "portfolio_id": str(portfolio_id),
        "change_type": change_type,
        "details": details,
    }

    # Log the portfolio change
    await log_activity(message=log_message, level="info", component="portfolio")
