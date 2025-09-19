from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.database import get_db
from app.models.incident import Incident
import datetime
from typing import Dict, List

router = APIRouter(prefix="/api", tags=["slametrics"])

@router.get("/slametrics")
async def sla_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident))
    incidents = result.scalars().all()

    response_durations = []
    resolution_durations = []
    total_closed = 0
    total_open = 0

    for inc in incidents:
        if inc.status in ["closed", "Закрыт"]:
            total_closed += 1
        else:
            total_open += 1

        if inc.first_response_at:
            diff = (inc.first_response_at - inc.created_at).total_seconds() / 60
            response_durations.append(diff)

        if inc.closed_at:
            diff = (inc.closed_at - inc.created_at).total_seconds() / 60
            resolution_durations.append(diff)

    avg_response = round(sum(response_durations) / len(response_durations), 2) if response_durations else 0
    avg_resolution = round(sum(resolution_durations) / len(resolution_durations), 2) if resolution_durations else 0

    return {
        "avg_response_minutes": avg_response,
        "avg_resolution_minutes": avg_resolution,
        "total_closed": total_closed,
        "total_open": total_open
    }

@router.get("/threat-level")
async def get_threat_level(
    period_days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Calculate threat level based on incidents in the specified period."""
    
    # Calculate date range
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=period_days)
    
    # Get incidents in the period
    result = await db.execute(
        select(Incident).where(
            and_(
                Incident.created_at >= start_date,
                Incident.created_at <= end_date
            )
        )
    )
    incidents = result.scalars().all()
    
    # Calculate metrics
    total_incidents = len(incidents)
    high_priority = len([i for i in incidents if i.priority == "high"])
    open_incidents = len([i for i in incidents if i.status == "open"])
    
    # Calculate threat level (0-100 scale)
    threat_score = 0
    
    # Base score from total incidents
    if total_incidents > 0:
        threat_score += min(total_incidents * 10, 40)  # Max 40 points for volume
    
    # High priority incidents weight more
    threat_score += high_priority * 20  # 20 points per high priority
    
    # Open incidents indicate ongoing threats
    threat_score += open_incidents * 5  # 5 points per open incident
    
    # Normalize to 0-100 scale
    threat_score = min(threat_score, 100)
    
    # Determine threat level category
    if threat_score >= 80:
        threat_level = "critical"
        color = "danger"
    elif threat_score >= 60:
        threat_level = "high"
        color = "warning"
    elif threat_score >= 40:
        threat_level = "medium"
        color = "info"
    elif threat_score >= 20:
        threat_level = "low"
        color = "success"
    else:
        threat_level = "minimal"
        color = "secondary"
    
    # Calculate trend (compare with previous period)
    prev_start = start_date - datetime.timedelta(days=period_days)
    prev_result = await db.execute(
        select(Incident).where(
            and_(
                Incident.created_at >= prev_start,
                Incident.created_at < start_date
            )
        )
    )
    prev_incidents = prev_result.scalars().all()
    prev_total = len(prev_incidents)
    
    trend = "stable"
    if total_incidents > prev_total * 1.2:
        trend = "increasing"
    elif total_incidents < prev_total * 0.8:
        trend = "decreasing"
    
    return {
        "threat_score": threat_score,
        "threat_level": threat_level,
        "color": color,
        "total_incidents": total_incidents,
        "high_priority": high_priority,
        "open_incidents": open_incidents,
        "period_days": period_days,
        "trend": trend,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat()
    }

@router.get("/incident-stats")
async def get_incident_stats(
    period_days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed incident statistics for dashboard."""
    
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=period_days)
    
    # Get incidents in the period
    result = await db.execute(
        select(Incident).where(
            and_(
                Incident.created_at >= start_date,
                Incident.created_at <= end_date
            )
        )
    )
    incidents = result.scalars().all()
    
    # Calculate statistics
    stats = {
        "total": len(incidents),
        "by_status": {},
        "by_priority": {},
        "by_day": {},
        "avg_response_time": 0,
        "avg_resolution_time": 0
    }
    
    response_times = []
    resolution_times = []
    
    for incident in incidents:
        # Status breakdown
        status = incident.status
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Priority breakdown
        priority = incident.priority
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # Daily breakdown
        day = incident.created_at.strftime("%Y-%m-%d")
        stats["by_day"][day] = stats["by_day"].get(day, 0) + 1
        
        # Response time
        if incident.first_response_at:
            response_time = (incident.first_response_at - incident.created_at).total_seconds() / 60
            response_times.append(response_time)
        
        # Resolution time
        if incident.closed_at:
            resolution_time = (incident.closed_at - incident.created_at).total_seconds() / 60
            resolution_times.append(resolution_time)
    
    # Calculate averages
    if response_times:
        stats["avg_response_time"] = round(sum(response_times) / len(response_times), 2)
    if resolution_times:
        stats["avg_resolution_time"] = round(sum(resolution_times) / len(resolution_times), 2)
    
    return stats
