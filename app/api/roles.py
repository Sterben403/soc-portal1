from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.role_request import RoleRequest
from app.models.user import User
from app.schemas.role_request import RoleRequestCreate, RoleRequestOut
from app.dependencies.auth import get_current_user
from app.security.keycloak import require_roles        # guard для админа
from app.security.keycloak_admin import assign_realm_role_to_email
from datetime import datetime

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/request", response_model=RoleRequestOut)
async def request_role(payload: RoleRequestCreate,
                       db: AsyncSession = Depends(get_db),
                       me: User = Depends(get_current_user)):
    # запретим дубликаты в pending
    q = await db.execute(select(RoleRequest).where(
        RoleRequest.user_id == me.id,
        RoleRequest.requested_role == payload.role,
        RoleRequest.status == "pending"
    ))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Заявка уже отправлена")

    rr = RoleRequest(user_id=me.id, requested_role=payload.role, status="pending")
    db.add(rr)
    await db.commit(); await db.refresh(rr)
    return rr

@router.get("/requests", response_model=list[RoleRequestOut], dependencies=[Depends(require_roles("admin"))])
async def list_requests(status: str = "pending", db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(RoleRequest).where(RoleRequest.status == status).order_by(RoleRequest.id.desc()))
    return q.scalars().all()

@router.get("/requests/count", dependencies=[Depends(require_roles("admin"))])
async def count_requests(status: str = "pending", db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(func.count()).select_from(RoleRequest).where(RoleRequest.status == status))
    return {"count": int(q.scalar() or 0)}

@router.post("/requests/{req_id}/approve", response_model=RoleRequestOut, dependencies=[Depends(require_roles("admin"))])
async def approve_request(req_id: int, db: AsyncSession = Depends(get_db)):
    rr = await db.get(RoleRequest, req_id)
    if not rr or rr.status != "pending":
        raise HTTPException(status_code=404, detail="Заявка не найдена или уже обработана")

    user = await db.get(User, rr.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    await assign_realm_role_to_email(user.email, rr.requested_role)

    rr.status = "approved"
    rr.decided_by = user.id  # при желании подставь id админа из токена
    rr.decided_at = datetime.utcnow()
    await db.commit(); await db.refresh(rr)
    return rr

@router.post("/requests/{req_id}/reject", response_model=RoleRequestOut, dependencies=[Depends(require_roles("admin"))])
async def reject_request(req_id: int, comment: str | None = None, db: AsyncSession = Depends(get_db)):
    rr = await db.get(RoleRequest, req_id)
    if not rr or rr.status != "pending":
        raise HTTPException(status_code=404, detail="Заявка не найдена или уже обработана")

    rr.status = "rejected"
    rr.comment = comment
    rr.decided_at = datetime.utcnow()
    await db.commit(); await db.refresh(rr)
    return rr
