from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.jobs.daily_report import generate_daily_reports
from app.jobs.ticket_sla import check_ticket_sla

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        generate_daily_reports,
        CronTrigger(hour=8, minute=0),  
        id="daily_report"
    )
    scheduler.add_job(
        check_ticket_sla,
        CronTrigger(hour="*", minute=0),  # проверка каждый час, в начале часа
       id="ticket_sla_breach"
    )
    scheduler.start()