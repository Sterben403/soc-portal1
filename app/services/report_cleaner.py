from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, delete
from datetime import datetime, timedelta
from app.models.report import ReportArchive
import os


async def cleanup_old_reports(db: AsyncSession):
    days = int(os.getenv("REPORT_RETENTION_DAYS", "30"))
    cutoff = datetime.utcnow() - timedelta(days=days)

    stmt = delete(ReportArchive).where(ReportArchive.generated_at < cutoff)
    await db.execute(stmt)
    await db.commit()