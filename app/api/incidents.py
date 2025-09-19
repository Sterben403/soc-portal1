from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import List, Dict

from app.db.database import SessionLocal
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentOut
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.models.incident_history import IncidentHistory
from app.services.notify import send_notification_event

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


async def get_db():
  async with SessionLocal() as session:
      yield session


# --- CREATE (analyst/manager; admin проходит в require_roles автоматически) ---
@router.post(
    "",
    response_model=IncidentOut,
    # Клиенты создавать не могут; аналитик/менеджер/админ — могут
    dependencies=[Depends(require_roles("analyst", "manager", "admin"))],
)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # client_id может отсутствовать в схеме IncidentCreate — берём аккуратно
    client_id = getattr(data, "client_id", None)

    # Временная логика: если client_id не передан — ставим текущего пользователя.
    # (Когда добавите поле выбора клиента на фронте — просто начнёт заполняться из формы.)
    if not client_id:
        client_id = user.id

    incident = Incident(
        title=data.title,
        description=data.description,
        priority=(getattr(data, "priority", None) or "medium"),
        client_id=client_id,
        created_by=user.id,
    )
    db.add(incident)
    await db.flush()

    db.add(IncidentHistory(
        incident_id=incident.id,
        user_id=user.id,
        action="created",
        details=None,
    ))

    await db.commit()
    await db.refresh(incident)

    await send_notification_event(
        "incident_created",
        f"Новый инцидент #{incident.id}: {incident.title}",
    )
    return incident


# --- LIST MINE / ALL (по ролям) ---
@router.get("/my", response_model=List[IncidentOut], dependencies=[Depends(require_roles("client", "analyst", "manager"))])
async def get_my_incidents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Incident)

    if (current_user.role or "").lower() == "client":
        stmt = stmt.where(Incident.client_id == current_user.id)
    elif (current_user.role or "").lower() in ("analyst", "manager", "admin"):
        # аналитик/менеджер/админ — видят всё
        pass
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(stmt.order_by(Incident.created_at.desc()))
    return result.scalars().all()


# --- GET ONE ---
@router.get("/{incident_id}", response_model=IncidentOut, dependencies=[Depends(require_roles("client", "analyst", "manager"))])
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if (user.role or "").lower() == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this incident")

    return incident


# --- CLOSE (analyst) ---
@router.post("/{incident_id}/close", response_model=IncidentOut, dependencies=[Depends(require_roles("analyst"))])
async def close_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status == "closed":
        raise HTTPException(status_code=400, detail="Incident already closed")

    incident.status = "closed"
    incident.closed_at = datetime.utcnow()
    db.add(incident)

    db.add(IncidentHistory(
        incident_id=incident.id,
        user_id=user.id,
        action="closed",
        details=None,
    ))

    await db.commit()
    await db.refresh(incident)

    await send_notification_event(
        "incident_closed",
        f"Инцидент #{incident.id} закрыт аналитиком",
    )
    return incident


# --- CONFIRM (owning client) ---
@router.post("/{incident_id}/confirm", response_model=IncidentOut, dependencies=[Depends(require_roles("client"))])
async def confirm_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.client_id != user.id and (user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Only the owning client can confirm")

    db.add(IncidentHistory(
        incident_id=incident.id,
        user_id=user.id,
        action="confirmed",
        details=None,
    ))
    await db.commit()
    await db.refresh(incident)

    await send_notification_event(
        "incident_confirmed",
        f"Инцидент #{incident.id} подтверждён клиентом",
    )
    return incident


# --- REOPEN (analyst) ---
@router.post("/{incident_id}/reopen", response_model=IncidentOut, dependencies=[Depends(require_roles("analyst"))])
async def reopen_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "open"
    db.add(incident)

    db.add(IncidentHistory(
        incident_id=incident.id,
        user_id=user.id,
        action="reopened",
        details=None,
    ))

    await db.commit()
    await db.refresh(incident)

    await send_notification_event(
        "incident_reopened",
        f"Инцидент #{incident.id} переоткрыт",
    )
    return incident


# --- HISTORY ---
@router.get("/{incident_id}/history", response_model=List[Dict], dependencies=[Depends(require_roles("client", "analyst", "manager"))])
async def get_incident_history(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if (user.role or "").lower() == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(IncidentHistory)
        .where(IncidentHistory.incident_id == incident_id)
        .order_by(IncidentHistory.timestamp.asc())
    )
    history = result.scalars().all()

    return [
        {
            "id": h.id,
            "user_id": h.user_id,
            "action": h.action,
            "details": h.details,
            "created_at": h.timestamp,   # фронт ждёт created_at
        }
        for h in history
    ]
