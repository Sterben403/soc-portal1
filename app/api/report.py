from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, datetime, timedelta
import io
from typing import Optional

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.reports.utils import (
    fetch_incidents_by_date,
    generate_pdf,
    generate_csv,
    generate_excel,
)
from app.services.email_sender import send_email_with_attachment
from app.models.report import ReportArchive, ReportFormat

router = APIRouter(prefix="/report", tags=["Reports"])


def check_report_access(user: User):
    if user.role not in ["analyst", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")


def resolve_range(start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
    """Если даты не заданы — используем последние 7 дней."""
    if start_date and end_date:
        return start_date, end_date
    today = date.today()
    return today - timedelta(days=7), today


@router.get("/pdf")
async def get_pdf_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_report_access(user)
    start_date, end_date = resolve_range(start_date, end_date)
    data = await fetch_incidents_by_date(db, start_date, end_date)
    pdf_bytes = generate_pdf(data, username=user.username)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=incident_report.pdf"},
    )


@router.get("/csv")
async def get_csv_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_report_access(user)
    start_date, end_date = resolve_range(start_date, end_date)
    data = await fetch_incidents_by_date(db, start_date, end_date)
    csv_bytes = generate_csv(data)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=incident_report.csv"},
    )


@router.get("/xlsx")
async def get_excel_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_report_access(user)
    start_date, end_date = resolve_range(start_date, end_date)
    data = await fetch_incidents_by_date(db, start_date, end_date)
    excel_bytes = generate_excel(data)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=incident_report.xlsx"},
    )


@router.post("/send")
async def send_report_to_email(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("pdf", enum=["pdf", "csv", "xlsx"]),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    check_report_access(user)
    start_date, end_date = resolve_range(start_date, end_date)
    data = await fetch_incidents_by_date(db, start_date, end_date)

    if format == "pdf":
        file_bytes = generate_pdf(data, username=user.username)
        mime = "application/pdf"
        filename = "incident_report.pdf"
    elif format == "csv":
        file_bytes = generate_csv(data)
        mime = "text/csv"
        filename = "incident_report.csv"
    else:
        file_bytes = generate_excel(data)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "incident_report.xlsx"

    new_report = ReportArchive(
        filename=filename,
        format=ReportFormat(format),
        content=file_bytes,
        generated_by_id=user.id,
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    await send_email_with_attachment(
        to_email=user.email,
        subject="Your SOC Report",
        body="Attached is the requested incident report.",
        filename=filename,
        file_bytes=file_bytes,
        mime_type=mime,
    )

    return {"message": f"Report sent to {user.email}"}


@router.get("/archive/{report_id}")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = await db.get(ReportArchive, report_id)
    if not report or (user.role != "manager" and report.generated_by_id != user.id):
        raise HTTPException(status_code=404, detail="Not found")

    media = {
        "pdf": "application/pdf",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }[report.format.value]

    return StreamingResponse(
        io.BytesIO(report.content),
        media_type=media,
        headers={"Content-Disposition": f"attachment; filename={report.filename}"},
    )


@router.get("/archive")
async def list_reports(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: Optional[ReportFormat] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "manager":
        stmt = select(ReportArchive)
    else:
        stmt = select(ReportArchive).where(ReportArchive.generated_by_id == user.id)

    if start_date:
        stmt = stmt.where(
            ReportArchive.generated_at >= datetime.combine(start_date, datetime.min.time())
        )
    if end_date:
        stmt = stmt.where(
            ReportArchive.generated_at <= datetime.combine(end_date, datetime.max.time())
        )
    if format:
        stmt = stmt.where(ReportArchive.format == format)

    stmt = stmt.order_by(ReportArchive.generated_at.desc())
    result = await db.execute(stmt)
    reports = result.scalars().all()

    return [
        {
            "id": r.id,
            "filename": r.filename,
            "format": r.format.value,
            "created_at": r.generated_at.isoformat(),
        }
        for r in reports
    ]
