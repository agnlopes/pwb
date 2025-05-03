from app.utils.logging import logger
from app.models.audit_log import AuditLog
from app.models.portfolio_ledger import PortfolioLedger
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime


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
    session.add(log_entry)
    await session.commit()

    logger.info(
        "User action logged",
        extra={
            "user_id": str(user_id),
            "action": action,
            "target_type": target_type,
            "target_id": str(target_id),
            "details": details,
        },
    )


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
    session.add(ledger_entry)
    await session.commit()

    logger.info(
        "Portfolio change recorded",
        extra={
            "portfolio_id": str(portfolio_id),
            "change_type": change_type,
            "details": details,
        },
    )
