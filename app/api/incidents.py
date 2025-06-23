from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/incidents", tags=["incidents"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=IncidentOut)
async def create_incident(data: IncidentCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    incident = Incident(**data.dict(), client_id=user.id)
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident

@router.get("/", response_model=list[IncidentOut])
async def get_all(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "analyst" or user.role == "manager":
        result = await db.execute(select(Incident))
    else:
        result = await db.execute(select(Incident).where(Incident.client_id == user.id))
    return result.scalars().all()

@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_status(incident_id: int, update: IncidentUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "analyst":
        raise HTTPException(status_code=403, detail="Only analysts can update incidents")

    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Not found")

    incident.status = update.status
    await db.commit()
    await db.refresh(incident)
    return incident