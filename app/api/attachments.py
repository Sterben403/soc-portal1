import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.models.attachment import Attachment
from app.models.message import Message
from app.models.incident import Incident
from app.schemas.attachment import AttachmentOut
from app.dependencies.auth import get_current_user
from app.models.user import User
from uuid import uuid4
from shutil import copyfileobj

UPLOAD_DIR = "uploads"

router = APIRouter(prefix="/attachments", tags=["attachments"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=AttachmentOut)
async def upload_file(
    message_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if file.size is not None and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    result = await db.execute(select(Incident).where(Incident.id == message.incident_id))
    incident = result.scalar()

    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        copyfileobj(file.file, buffer)

    attachment = Attachment(
        message_id=message_id,
        file_path=path,
        file_name=file.filename
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment

@router.get("/{attachment_id}")
async def download_file(attachment_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Attachment).where(Attachment.id == attachment_id))
    attachment = result.scalar()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    result = await db.execute(select(Message).where(Message.id == attachment.message_id))
    message = result.scalar()
    result = await db.execute(select(Incident).where(Incident.id == message.incident_id))
    incident = result.scalar()

    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

    return FileResponse(attachment.file_path, filename=attachment.file_name)