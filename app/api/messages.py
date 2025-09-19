import os
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.message import Message
from app.schemas.message import MessageOut

router = APIRouter(prefix="/api/messages", tags=["messages"])

UPLOAD_DIR = "attachments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_db():
    async with SessionLocal() as session:
        yield session

def _check_access(user: User, incident: Incident):
    # manager — чтение/запись оставляем; при желании сузить
    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

@router.post("", response_model=MessageOut)
async def send_message(
    incident_id: int = Form(...),
    # поддерживаем и text, и message — фронт шлёт "message"
    text: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Менеджеру запрещаем писать сообщения (только чтение по ТЗ)
    if user.role == "manager":
        raise HTTPException(status_code=403, detail="Managers have read-only access")
    # 1) проверка инцидента и доступа
    res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = res.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    _check_access(user, incident)

    # 2) нормализуем текст
    content = (text or message or "").strip()
    if not content and not file:
        raise HTTPException(status_code=400, detail="Empty message")

    # 3) если есть файл — сохраняем
    filename = None
    if file:
        allowed = {"application/pdf", "image/png", "image/jpeg"}
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Invalid file type")
        data = await file.read()
        if len(data) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(data)

    # 4) создаём сообщение
    msg = Message(
        incident_id=incident_id,
        text=content,
        sender_id=user.id,
        sender_role=user.role,
        attachment=filename,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # 5) отдаём форму, которую ждёт фронт (message вместо text)
    return {
        "id": msg.id,
        "incident_id": msg.incident_id,
        "sender_id": msg.sender_id,
        "sender_role": msg.sender_role,
        "message": msg.text,          # ключевой момент
        "created_at": msg.created_at,
        "attachment": msg.attachment,
    }

@router.get("/{incident_id}", response_model=List[MessageOut])
async def get_messages(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1) проверка инцидента и доступа
    res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = res.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    _check_access(user, incident)

    # 2) сообщения
    res = await db.execute(
        select(Message)
        .where(Message.incident_id == incident_id)
        .order_by(Message.created_at.asc())
    )
    rows = res.scalars().all()

    # 3) маппим под фронт
    return [
        {
            "id": m.id,
            "incident_id": m.incident_id,
            "sender_id": m.sender_id,
            "sender_role": m.sender_role,
            "message": m.text,
            "created_at": m.created_at,
            "attachment": m.attachment,
        }
        for m in rows
    ]
