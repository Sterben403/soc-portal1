import os
import shutil
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
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Header

# Use consistent directory for attachments and ensure it exists
dir_path = os.path.join(os.getcwd(), 'attachments')
os.makedirs(dir_path, exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

router = APIRouter(prefix="/attachments", tags=["attachments"])

async def get_db():
    async with SessionLocal() as session:
        yield session

router.post("/", response_model=AttachmentOut)
async def upload_file(
    message_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check file size
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    # Verify incident ownership
    result = await db.execute(select(Incident).where(Incident.id == message.incident_id))
    incident = result.scalar()
    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

    # Save file
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    path = os.path.join(dir_path, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Persist attachment record
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
async def download_file(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch record
    result = await db.execute(select(Attachment).where(Attachment.id == attachment_id))
    attachment = result.scalar()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    # Check ownership
    result = await db.execute(select(Message).where(Message.id == attachment.message_id))
    message = result.scalar()
    result = await db.execute(select(Incident).where(Incident.id == message.incident_id))
    incident = result.scalar()
    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")
    # Serve file
    if not os.path.isfile(attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        path=attachment.file_path,
        media_type="application/octet-stream",
        filename=attachment.file_name
    )
