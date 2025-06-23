from fastapi import FastAPI
from app.db.database import init_db
from app.api import auth
from app.api import protected
from app.api import incidents
from app.api import messages
from app.api import attachments
from app.api import tickets
from app.api import notifications
from fastapi import FastAPI
from app.api import report  
from app.jobs.scheduler import start_scheduler

app = FastAPI()
app.include_router(report.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(report.router, prefix="/report")
app.include_router(protected.router)
app.include_router(incidents.router)
app.include_router(messages.router)
app.include_router(attachments.router)
app.include_router(tickets.router)
app.include_router(notifications.router)
@app.on_event("startup")
async def on_startup():
    await init_db()
    start_scheduler()
app.include_router(auth.router)