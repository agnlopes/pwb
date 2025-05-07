from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.utils.logging import logger

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.start()
    scheduler.add_job(
        func=refresh_market_data,
        trigger=IntervalTrigger(seconds=30),
        id="refresh_market_data",
        name="Refresh market data every 30s",
        replace_existing=True,
    )


def refresh_market_data():
    log_activity("Scheduled job: Refreshing market data", level="info")
