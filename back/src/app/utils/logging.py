import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession  # type: ignore

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.portfolio_ledger import PortfolioLedger

# Create log directory if it doesn't exist
LOG_DIR = settings.LOG_DIR
LOG_FILE = settings.LOG_FILE
os.makedirs(LOG_DIR, exist_ok=True)


# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


# System file handler (all logs)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(JsonFormatter())

# Stdout handler (warnings and above)
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.WARNING)
stdout_handler.setFormatter(JsonFormatter())

# Main app logger
logger = logging.getLogger("pwb")
logger.propagate = False


# Add handlers to the logger
async def log_activity(
    message: dict = {},
    level: str = "info",
):
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

    # Log the activity
    logger.log(loggers[level], json.dumps(message))


# Add handlers to the user action logger
async def log_user_action(
    session: AsyncSession,
    user_id: UUID,
    action: str,
    target_type: str,
    target_id: UUID,
    details: dict | None = None,
) -> None:
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        timestamp=datetime.utcnow(),
    )

    # Commit the user  action entry
    session.add(log_entry)
    await session.commit()

    # Create a log message
    log_message = {
        "type": "user_action",
        "user_id": str(user_id),
        "action": action,
        "target_type": target_type,
        "target_id": str(target_id),
        "details": details,
    }

    # Log the user action
    await log_activity(message=log_message, level="info")


# Add handlers to the portfolio change logger
async def record_portfolio_change(
    session: AsyncSession,
    portfolio_id: UUID,
    change_type: str,
    details: dict,
) -> None:
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
    await log_activity(message=log_message, level="info")
