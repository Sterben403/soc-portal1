from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/secure", tags=["secure"])

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }

@router.get("/analyst-only")
async def analyst_route(user: User = Depends(require_role("analyst"))):
    return {"message": f"Hello, SOC Analyst {user.username}"}

@router.get("/client-only")
async def client_route(user: User = Depends(require_role("client"))):
    return {"message": f"Hello, client {user.username}"}