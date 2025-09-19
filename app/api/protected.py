from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User

router = APIRouter(prefix="/secure", tags=["secure"])

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}

@router.get("/analyst-only")
async def analyst_route(user: User = Depends(require_roles("analyst"))):
    return {"message": f"Hello, SOC Analyst {user.username}"}

@router.get("/client-only")
async def client_route(user: User = Depends(require_roles("client"))):
    return {"message": f"Hello, client {user.username}"}

@router.get(
    "/audit",
    dependencies=[Depends(require_roles("manager"))],
    summary="Просмотр audit-логов (только для менеджера)"
)
async def list_audit_logs():
    # Здесь раньше был пустой SELECT -> 500. Оставлю заглушку.
    return {"items": []}
