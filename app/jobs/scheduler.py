from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.jobs.daily_report import generate_daily_reports

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        generate_daily_reports,
        CronTrigger(hour=8, minute=0),  # каждый день в 08:00
        id="daily_report"
    )
    scheduler.start()