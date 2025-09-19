from app.models.report import ReportArchive, ReportFormat

from app.db.database import SessionLocal
from app.models.user import User
from app.services.email_sender import send_email_with_attachment
from app.reports.utils import generate_pdf, fetch_incidents_by_date

from datetime import date, timedelta
from sqlalchemy import select

async def generate_daily_reports():
    print("[*] Running daily report generation...")
    async with SessionLocal() as db:
        today = date.today()
        yesterday = today - timedelta(days=1)

        result = await db.execute(
            select(User).where(User.role.in_(["analyst", "manager"]))
        )
        users = result.scalars().all()

        for user in users:
            data = await fetch_incidents_by_date(db, yesterday, today)
            file_bytes = generate_pdf(data, username=user.username)

            archive = ReportArchive(
                filename=f"daily_report_{today}.pdf",
                format=ReportFormat.pdf,
                content=file_bytes,
                generated_by_id=user.id
            )
            db.add(archive)
            await db.commit()
            await db.refresh(archive)

            await send_email_with_attachment(
                to_email=user.email,
                subject="Daily SOC Report",
                body="Your daily report is attached.",
                filename=archive.filename,
                file_bytes=file_bytes,
                mime_type="application/pdf"
            )

        print("[+] Daily reports sent.")